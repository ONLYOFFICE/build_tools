LIB_EXT=.so
core_windows {
	LIB_EXT=.dll
}
core_mac {
	LIB_EXT=.dylib
}

EXE_EXT=
core_windows {
	EXE_EXT=.exe
}

LIB_PRE=
!core_windows {
	LIB_PRE=lib
}

CALL_COMMAND=
core_windows {
	CALL_COMMAND="call "
}

defineTest(copyDirectory) {
	src = $$1
	dst = $$2
	
	win32:src ~= s,/,\\,g
	win32:dst ~= s,/,\\,g
	
	system($$QMAKE_COPY_DIR $$shell_quote($$src) $$shell_quote($$dst) $$escape_expand(\\n\\t))
}

defineTest(copyFile) {
	file = $$1
	dir = $$2
	
	win32:file ~= s,/,\\,g
	win32:dir ~= s,/,\\,g
	
	system($$QMAKE_COPY_FILE $$shell_quote($$file) $$shell_quote($$dir) $$escape_expand(\\n\\t))
}

defineTest(copyLib) {
	dir1 = $$1
	dir2 = $$2
	lib = $$3

	win32:dir1 ~= s,/,\\,g
	win32:dir2 ~= s,/,\\,g

	LIBNAME=$$join(lib, lib, $$LIB_PRE, $$LIB_EXT)

	system($$QMAKE_COPY_FILE $$shell_quote($$dir1/$$LIBNAME) $$shell_quote($$dir2/$$LIBNAME) $$escape_expand(\\n\\t))
}

defineTest(removeFile) {
	file = $$1
		
	win32:file ~= s,/,\\,g

	system($$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
}

defineTest(createDirectory) {
	dir = $$1
		
	win32:dir ~= s,/,\\,g

	core_windows {
		system($$QMAKE_CHK_DIR_EXISTS $$shell_quote($$dir) $$QMAKE_MKDIR $$shell_quote($$dir) $$escape_expand(\\n\\t))
	} else {
		system($$QMAKE_MKDIR $$shell_quote($$dir) $$escape_expand(\\n\\t))
	}
}

defineTest(removeDirectory) {
    dir = $$1
		
	win32:dir ~= s,/,\\,g
	
	core_windows {
		system($$QMAKE_CHK_DIR_EXISTS $$shell_quote($$dir) $$QMAKE_MKDIR $$shell_quote($$dir) $$escape_expand(\\n\\t))
	} else {
		system($$QMAKE_MKDIR $$shell_quote($$dir) $$escape_expand(\\n\\t))
	}

	core_windows {
		system(rmdir /S /Q $$shell_quote($$dir) $$escape_expand(\\n\\t))
	} else {
		system(rm -rf $$shell_quote($$dir) $$escape_expand(\\n\\t))
	}
}

defineTest(copyQtLib) {
	createDirectory($$2);

	core_windows {
		copyLib($$QT_CURRENT, $$2, $$1$$LIB_EXT)
	}
	core_linux {
		file=$$1
		lib1=$$join(file, file, "lib", ".so.$$QT_VERSION")
		lib2=$$join(file, file, "lib", ".so")
		system($$QMAKE_COPY_FILE $$shell_quote($$QT_CURRENT/../lib/$$lib1) $$shell_quote($$2/$$lib2) $$escape_expand(\\n\\t))
	}
}

defineTest(copyQtPlugin) {
	copyDirectory($$1, $$2)
}

defineTest(runNPM) {
	dir = $$1

	win32:dir ~= s,/,\\,g

	system($$CALL_COMMAND npm --prefix $$shell_quote($$dir) install $$shell_quote($$dir) $$escape_expand(\\n\\t))
}

defineTest(runNPM2) {
	dir = $$1

	win32:dir ~= s,/,\\,g

	system($$CALL_COMMAND npm --prefix $$shell_quote($$dir) install $$shell_quote($$dir) $$shell_quote(git://github.com/gruntjs/grunt-contrib-uglify.git$${LITERAL_HASH}harmony) $$escape_expand(\\n\\t))
}

defineTest(gruntInterface) {
	dir = $$1

	win32:dir ~= s,/,\\,g

	system($$CALL_COMMAND grunt --force --base $$shell_quote($$dir) $$escape_expand(\\n\\t))
}

defineTest(gruntBuilder) {
	dir = $$1
		
	win32:dir ~= s,/,\\,g

	system($$CALL_COMMAND grunt --base $$shell_quote($$dir) --level=ADVANCED $$escape_expand(\\n\\t))
}

defineTest(gruntDesktop) {
	dir = $$1

	win32:dir ~= s,/,\\,g

	system($$CALL_COMMAND grunt --base $$shell_quote($$dir) --level=ADVANCED --desktop=true $$escape_expand(\\n\\t))
}
