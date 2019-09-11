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

	LIBNAME=$$join(lib, lib, "$$LIB_PRE", "$$LIB_EXT")

	core_windows {
		dir1=$$dir1/$$LIBNAME
		dir2=$$dir2/$$LIBNAME
		dir1 ~= s,/,\\,g
		dir2 ~= s,/,\\,g

		system($$QMAKE_COPY_FILE $$shell_quote($$dir1) $$shell_quote($$dir2) $$escape_expand(\\n\\t))
	} else {
		system($$QMAKE_COPY_FILE $$shell_quote($$dir1/$$LIBNAME) $$shell_quote($$dir2/$$LIBNAME) $$escape_expand(\\n\\t))
	}
}

defineTest(removeFile) {
	file = $$1
		
	win32:file ~= s,/,\\,g

	core_windows {
		system(if exist $$shell_quote($$file) $$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
	} else {
		system($$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
	}	
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
		copyLib($$QT_CURRENT, $$2, $$1)
	}
	core_linux {
		file=$$1
		lib1=$$join(file, file, "lib", ".so.$$QT_VERSION")
		lib2=$$join(file, file, "lib", ".so.$$QT_MAJOR_VERSION")
		system($$QMAKE_COPY_FILE $$shell_quote($$QT_CURRENT/../lib/$$lib1) $$shell_quote($$2/$$lib2) $$escape_expand(\\n\\t))
	}
}

defineTest(copyQtPlugin) {
	copyDirectory($$1, $$2)

	core_windows {
		qt_libs = $$files($$2/*, false)
		win32:qt_libs ~= s,/,\\,g
		
		for(qt_lib, qt_libs) {
			qt_lib_test=$$qt_lib
			qt_lib_test=$$replace(qt_lib_test, .dll, d.dll)
			system(if exist $$shell_quote($$qt_lib_test) $$QMAKE_DEL_FILE $$shell_quote($$qt_lib_test) $$escape_expand(\\n\\t))
		}
	}
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

defineTest(replaceInFile) {
	file = $$1
	win32:file ~= s,/,\\,g

	core_windows {
		system("call powershell -Command \"(Get-Content '$$file') -replace '$$2', '$$3' | Set-Content '$$file'\"")
	} else {
		system(sed -i -e $$shell_quote(s|$$2|$$3|g) $$shell_quote($$file))
	}
}

defineTest(checkICU_common) {
	testDir = $$1
	outputDir = $$2

	exists($$testDir/libicu*) {
		system(cp -f -av "$$testDir/libicui18n*" $$shell_quote($$outputDir/) $$escape_expand(\\n\\t))
		system(cp -f -av "$$testDir/libicuuc*" $$shell_quote($$outputDir/) $$escape_expand(\\n\\t))
		system(cp -f -av "$$testDir/libicudata*" $$shell_quote($$outputDir/) $$escape_expand(\\n\\t))
		return(true)
	}
	return(false)
}

defineTest(copyQtICU) {
	testDir = $$1
	outputDir = $$2

	checkICU_common($$testDir, $$outputDir) {
		return(true)
	}

	checkICU_common(/lib, $$outputDir) {
		return(true)
	}

	checkICU_common(/lib/x86_64-linux-gnu, $$outputDir) {
		return(true)
	}

	checkICU_common(/lib64, $$outputDir) {
		return(true)
	}

	checkICU_common(/lib64/x86_64-linux-gnu, $$outputDir) {
		return(true)
	}

	checkICU_common(/usr/lib, $$outputDir) {
		return(true)
	}

	checkICU_common(/usr/lib/x86_64-linux-gnu, $$outputDir) {
		return(true)
	}

	checkICU_common(/usr/lib64, $$outputDir) {
		return(true)
	}

	checkICU_common(/usr/lib64/x86_64-linux-gnu, $$outputDir) {
		return(true)
	}

	checkICU_common(/lib/i386-linux-gnu, $$outputDir) {
		return(true)
	}

	checkICU_common(/usr/lib/i386-linux-gnu, $$outputDir) {
		return(true)
	}

	return(false)
}
