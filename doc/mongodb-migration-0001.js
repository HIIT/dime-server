use dime;

db.zgEvent.update({ '_class': "fi.hiit.dime.data.ZgEvent" }, { $set: { '_class': "fi.hiit.dime.data.DesktopEvent" } }, { multi:true } );
db.zgSubject.update({ '_class': "fi.hiit.dime.data.ZgSubject" }, { $set: { '_class': "fi.hiit.dime.data.Document" } }, { multi:true } );
db.zgSubject.dropIndexes()
db.zgSubject.update({}, { $rename: {"text": "plainTextContent"} }, false, true);
db.zgEvent.renameCollection("event");
db.zgSubject.renameCollection("informationElement");

db.event.update({}, { $rename: {"interpretation": "type"} }, false, true);
db.informationElement.update({}, { $rename: {"manifestation": "isStoredAs"} }, false, true);
db.informationElement.update({}, { $rename: {"interpretation": "type"} }, false, true);
db.informationElement.update({}, { $rename: {"mimetype": "mimeType"} }, false, true);

db.event.update({}, { $rename: {"subject": "targettedResource"} }, false, true);

db.event.update({}, { $rename: {"time_created": "timeCreated"} }, false, true);
db.event.update({}, { $rename: {"time_modified": "timeModified"} }, false, true);

db.informationElement.update({}, { $rename: {"time_created": "timeCreated"} }, false, true);
db.informationElement.update({}, { $rename: {"time_modified": "timeModified"} }, false, true);


db.event.update({}, { $rename: {"timestamp": "start"} }, false, true);
