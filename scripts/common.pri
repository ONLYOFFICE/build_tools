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

defineTest(removeFile) {
    file = $$1
		
    win32:file ~= s,/,\\,g
	
	system($$QMAKE_DEL_FILE $$shell_quote($$file) $$escape_expand(\\n\\t))
}

defineTest(createDirectory) {
    dir = $$1
		
    win32:dir ~= s,/,\\,g
	
	system($$QMAKE_CHK_DIR_EXISTS $$shell_quote($$dir) $$QMAKE_MKDIR $$shell_quote($$dir) $$escape_expand(\\n\\t))
}

defineTest(removeDirectory) {
    dir = $$1
		
    win32:dir ~= s,/,\\,g
	
	system($$QMAKE_DEL_DIR $$shell_quote($$dir) $$escape_expand(\\n\\t))
}

defineTest(copyQtPlugin) {
    createDirectory($$2);
	copyFile($$1/*$$LIB_EXT, $$2/.)
}

#copyFile($$PWD/path_to_file_1, $$PWD/path_to_file_2)
#copyDir($$PWD/path_to_folder_1, $$PWD/path_to_folder_2)
#copyFile($$PWD/path_to_folder/*, $$PWD/path_to_folder/.)

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