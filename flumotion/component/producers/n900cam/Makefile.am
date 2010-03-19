include $(top_srcdir)/common/python.mk

component_PYTHON = __init__.py n900cam.py
componentdir = $(libdir)/flumotion/python/flumotion/component/producers/n900cam
component_DATA = \
	n900cam.xml

clean-local:
	rm -rf *.pyc *.pyo

EXTRA_DIST = $(component_DATA)
