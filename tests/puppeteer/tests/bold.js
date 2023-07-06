Tester.load("path_to_file");
Tester.waitEditor();

// down Enter
Tester.keyClick("Enter");

// type text
Tester.input("Hello World!");

Tester.keyPress("ArrowLeft");
Tester.keyDown("Shift");
for (let i = 0; i < 5; i++)
  Tester.keyPress("ArrowLeft");
Tester.keyUp("Shift");

// bold
Tester.click("id-toolbar-btn-bold");
// italic
Tester.mouseClick(115, 105);

// if needed
Tester.waitAutosave();

Tester.downloadFile("docx", "./work_directory/new.docx")
Tester.downloadFile("odt", "./work_directory/new.odt")

Tester.close(true);
