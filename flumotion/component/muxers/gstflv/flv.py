# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4
#
# Flumotion - a streaming media server
# Copyright (C) 2004,2005,2006,2007 Fluendo, S.L. (www.fluendo.com).
# All rights reserved.

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE.GPL" in the source distribution for more information.

# Licensees having purchased or holding a valid Flumotion Advanced
# Streaming Server license may use this file in accordance with the
# Flumotion Advanced Streaming Server Commercial License Agreement.
# See "LICENSE.Flumotion" in the source distribution for more information.

# Headers in this file shall remain intact.

import gst
from twisted.internet import defer

from flumotion.component import feedcomponent

class Flv(feedcomponent.MultiInputParseLaunchComponent):
    checkTimestamp = True

    def get_muxer_string(self, properties):
        muxer = 'flvmux name=muxer is-live=True'
        return muxer

    def get_pipeline_string(self, properties):
        eaters = self.config.get('eater', {})
        sources = self.config.get('source', [])
        if eaters == {} and sources != []:
            # for upgrade without manager restart
            feeds = []
            for feed in sources:
                if not ':' in feed:
                    feed = '%s:default' % feed
                feeds.append(feed)
            eaters = {'default': [(x, 'default') for x in feeds]}

        pipeline = ''
        for e in eaters:
            for feed, alias in eaters[e]:
                pipeline += '@ eater:%s @ ' % alias

        pipeline += self.get_muxer_string(properties) + ' '
        return pipeline

    def configure_pipeline(self, pipeline, properties):
        self.fired_eaters = 0
        self._probes = {} # depay element -> id
        def buffer_probe_cb(a, b, depay, identity):
            pad = depay.get_pad("src")
            caps = pad.get_negotiated_caps()
            if not caps:
                return False
            muxer = self.pipeline.get_by_name("muxer")
            if "video" in caps.to_string():
                vpad = muxer.get_request_pad("video")
                identity.get_pad("src").link(vpad)
            elif "audio" in caps.to_string():
                apad = muxer.get_request_pad("audio")
                identity.get_pad("src").link(apad)
            depay.get_pad("src").remove_buffer_probe(self._probes[depay])
            identity.get_pad("src").set_blocked_async(True, self.is_blocked_cb)
            return True

        for e in self.eaters.values():
            identity = self.get_element(e.elementName + '-identity')
            depay = self.get_element(e.depayName)
            self._probes[depay] = \
                depay.get_pad("src").add_buffer_probe(
                    buffer_probe_cb, depay, identity)

    def is_blocked_cb(self, pad, is_blocked):
        if is_blocked:
            self.fired_eaters = self.fired_eaters + 1
            if self.fired_eaters == len(self.eaters):
                self.debug("All pads are now blocked")
                for e in self.eaters.values():
                    identity = self.get_element(e.elementName + '-identity')
                    identity.get_pad("src").set_blocked_async(False,
                        self.is_blocked_cb)
