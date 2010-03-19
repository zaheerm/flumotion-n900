include $(top_srcdir)/common/python.mk
include $(top_srcdir)/common/trial.mk

TRIAL_ENV = $(top_builddir)/env

BUILT_SOURCES = setup.py
CLEANFILES = $(BUILT_SOURCES)

EXTRA_DIST = 				\
	__init__.py			\
	common.py

check-local: trial
