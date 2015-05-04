use dime;
db.zgEvent.update({ '_class': "fi.hiit.dime.data.ZgEvent" }, { $set: { '_class': "fi.hiit.dime.data.DocumentEvent" } }, { multi:true } );
db.zgSubject.update({ '_class': "fi.hiit.dime.data.ZgSubject" }, { $set: { '_class': "fi.hiit.dime.data.Document" } }, { multi:true } );
db.zgSubject.dropIndexes()
db.zgSubject.update({}, { $rename: {"text": "plainTextContent"} }, false, true);
db.zgEvent.renameCollection("event");
db.zgSubject.renameCollection("informationElement");
