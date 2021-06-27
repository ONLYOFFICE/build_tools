# must setup CORE_ROOT_DIR before including

include($$CORE_ROOT_DIR/Common/base.pri)

MAKEFILE=makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX
PRO_SUFFIX=$$CORE_BUILDS_PLATFORM_PREFIX

core_debug {
	MAKEFILE=$$join(MAKEFILE, , , "_debug_")
	PRO_SUFFIX=$$join(PRO_SUFFIX, , , "_debug_")
}
build_xp {
	MAKEFILE=$$join(MAKEFILE, , , "_xp")
	PRO_SUFFIX=$$join(PRO_SUFFIX, , , "_xp")
}
OO_BRANDING_SUFFIX = $$(OO_BRANDING)
!isEmpty(OO_BRANDING_SUFFIX) {
	PRO_SUFFIX=$$join(PRO_SUFFIX, , , "$$OO_BRANDING_SUFFIX")
	MAKEFILE=$$join(MAKEFILE, , , "$$OO_BRANDING_SUFFIX")
}

message(current_makefile)
message($$MAKEFILE)

CONFIG += ordered

defineTest(removeFile) {
	file = $$1	
	win32:file ~= s,/,\\,g
	core_windows {
		system(if exist $$shell_quote($$file) $$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
	} else {
		system($$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
	}
}
defineTest(qmakeClear) {
	dir = $$1
	name = $$2
	removeFile($$1/Makefile.$$2$$PRO_SUFFIX)
	removeFile($$1/.qmake.stash)
}

# addSubProject() - adds project to SUBDIRS, creates variables associated with the project(file, makefile, depends)
# Arg1 - Project name
# Arg2 - Qmake file of project
# Arg3(optional) - Project dependencies
defineTest(addSubProject) {
	pro_name = $$1
	pro_file = $$2
	pro_depends = $$3
	isEmpty(pro_name):error(Sub-project name is not defined.)
	isEmpty(pro_file):error(Qmake file of sub-project \'$$pro_name\' is not defined.)
	!exists($$pro_file):error(Sub-project qmake file \'$$pro_file\' is not exists.)
	path = $$section(pro_file, /, 0, -2)
	ext_name = $$section(pro_file, /, -1, -1)
	name = $$section(ext_name, ., 0, 0)
	SUBDIRS += $$pro_name
	export(SUBDIRS)
	$${pro_name}.file = $$pro_file
	export($${pro_name}.file)
	$${pro_name}.makefile = $$path/Makefile.$$name$$PRO_SUFFIX
	export($${pro_name}.makefile)
	!isEmpty(pro_depends) {
		$${pro_name}.depends = $$pro_depends
		export($${pro_name}.depends)
	}
	# remove makefile
	qmakeClear($$path, $$name)
}
