/*
  Copyright (c) 2015 University of Helsinki

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

package fi.hiit.dime;

import fi.hiit.dime.data.*;
import fi.hiit.dime.util.RandomPassword;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import static org.junit.Assert.*;
import static org.hamcrest.CoreMatchers.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;


/**
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@RunWith(SpringJUnit4ClassRunner.class)
public class DataControllerTest extends RestTest {
    private static final double DELTA = 1e-10;

    /**
       Tests uploading event
       - checks that stubs work (if second upload gets expanded)
       - checks that specifying @type works
    */
    @Test
    public void testEventUpload() throws Exception {
        RandomPassword rand = new RandomPassword();

        // Create a document
        Document doc = new Document();
        doc.uri = "http://www.example.com/hello.txt";
        doc.plainTextContent = "Hello, world";
        doc.mimeType = "text/plain";
        doc.appId = rand.getPassword(20, false, false);

        // Create feedback, with document embedded
        FeedbackEvent event1 = new FeedbackEvent();
        event1.value = 0.42;
        event1.targettedResource = doc;

        dumpData("Event to be uploaded to " + eventApi, event1);

        FeedbackEvent outEvent1 = uploadEvent(event1, FeedbackEvent.class);

        assertEquals(event1.value, outEvent1.value, DELTA);

        dumpData("Event received back from server:", outEvent1);

        Document outDoc1 = (Document)outEvent1.targettedResource;
        assertEquals(doc.uri, outDoc1.uri);
        assertEquals(doc.plainTextContent, outDoc1.plainTextContent);
        assertEquals(doc.mimeType, outDoc1.mimeType); 

        // Create a "stub" document, i.e. that refers to the
        // previously uploaded one
        InformationElement stubDoc = InformationElement.makeStub(outDoc1);

        // Create feedback with the stub document
        FeedbackEvent event2 = new FeedbackEvent();
        event2.value = 0.89;
        event2.targettedResource = stubDoc;

        dumpData("Event with stub to be uploaded to " + eventApi, event2);
        
        FeedbackEvent outEvent2 = uploadEvent(event2, FeedbackEvent.class);
        assertEquals(event2.value, outEvent2.value, DELTA);

        dumpData("Second event received back from server:", outEvent2);

        // This checks that the stub has been "filled in" with the
        // missing info
        Document outDoc2 = (Document)outEvent2.targettedResource;
        assertEquals(outDoc1.getId(), outDoc2.getId());
        assertEquals(doc.uri, outDoc2.uri);
        assertEquals(doc.mimeType, outDoc2.mimeType);

        // Test using stub with appId

        // Create a "stub" document, i.e. that refers to the
        // previously uploaded one
        InformationElement stubDoc2 = new InformationElement();
        stubDoc2.appId = doc.appId;

        // Create feedback with the stub document
        FeedbackEvent event3 = new FeedbackEvent();
        event3.value = 0.56;
        event3.targettedResource = stubDoc2;

        dumpData("Event with appId stub to be uploaded to " + eventApi, event3);
        
        FeedbackEvent outEvent3 = uploadEvent(event3, FeedbackEvent.class);

        // Checks to ensure returned object is the same as uploaded
        assertEquals(event3.value, outEvent3.value, DELTA);

        dumpData("Second event received back from server:", outEvent2);

        // This checks that the appId-based stub has been "filled in"
        // with the missing info
        Document outDoc3 = (Document)outEvent3.targettedResource;
        assertEquals(outDoc1.getId(), outDoc3.getId());
        assertEquals(doc.appId, outDoc3.appId);
        assertEquals(doc.uri, outDoc3.uri);
        assertEquals(doc.mimeType, outDoc3.mimeType);

        // Test retrieving the events based on the document id
        FeedbackEvent[] getEvents = 
            getData(eventsApi + "?elemId=" + outDoc1.getId(), FeedbackEvent[].class);
        
        dumpData("Events retrieved by element id:", getEvents);

        assertEquals(3, getEvents.length);
        for (FeedbackEvent e : getEvents) {
            assertThat(e.getId(), anyOf(is(outEvent1.getId()),
                                        is(outEvent2.getId()),
                                        is(outEvent3.getId())));
            assertThat(e.value, anyOf(is(outEvent1.value),
                                      is(outEvent2.value),
                                      is(outEvent3.value)));
        }

    }

    /**
       Test uploading MessageEvent
     */
    @Test
    public void testMessageEvent() throws Exception {
        // Create a message event
        Message msg = createTestEmail();
        MessageEvent event1 = new MessageEvent();
        event1.targettedResource = msg;

        dumpData("Event to be uploaded to " + eventApi, event1);

        MessageEvent outEvent1 = uploadEvent(event1, MessageEvent.class);

        // Checks to ensure returned object is the same as uploaded
        dumpData("Event received back from server:", outEvent1);

        Message outMsg1 = (Message)outEvent1.targettedResource;
        assertEquals(msg.date, outMsg1.date);
        assertEquals(msg.subject, outMsg1.subject);
        assertEquals(msg.fromString, outMsg1.fromString); 
        assertEquals(msg.toString, outMsg1.toString);
        assertEquals(msg.ccString, outMsg1.ccString);

        String textContent = msg.subject + "\n\n" + msg.plainTextContent;
        assertEquals(textContent, outMsg1.plainTextContent); 
        assertEquals(msg.rawMessage, outMsg1.rawMessage); 
    }

    /**
       Tests uploading multiple heterogeneous events, 
       tests event reading interface
    */
    @Test
    public void testEventGet() throws Exception {
        // First upload three events of different types
        Event[] events = new Event[4];

        Document doc1 = new Document();
        doc1.uri = "http://www.example.com/hello.txt";
        doc1.plainTextContent = "Hello, world";
        doc1.mimeType = "text/plain";
        doc1.addTag("tag1");
        doc1.addTag("tag2");
        doc1.addTag("tag1");
        FeedbackEvent event1 = new FeedbackEvent();
        event1.value = 0.42;
        event1.targettedResource = doc1;
        event1.actor = "TestActor1";
        events[0] = event1;

        SearchEvent event2 = new SearchEvent();
        event2.query = "some search query";
        event2.actor = "TestActor1";
        event2.addTag("foo");
        events[1] = event2;

        SearchEvent event3 = new SearchEvent();
        event3.query = "some search query";
        event3.actor = "TestActor2";
        events[2] = event3;

        // Create a message event
        Message emailMsg = createTestEmail();
        emailMsg.addTag("tag2");
        
        MessageEvent event4 = new MessageEvent();
        event4.targettedResource = emailMsg;
        events[3] = event4;
    
        dumpData("testEventGet: events to be uploaded to " + eventsApi, events);

        Event[] outEvents = uploadEvents(events, Event[].class);

        // Checks to ensure returned object is the same as uploaded
        assertEquals(events.length, outEvents.length);

        FeedbackEvent outEvent1 = (FeedbackEvent)outEvents[0];
        assertEquals(event1.value, outEvent1.value, DELTA);
        Document origDoc = (Document)event1.targettedResource;
        Document uploadDoc = (Document)outEvent1.targettedResource;
        assertEquals(origDoc.uri, uploadDoc.uri);

        SearchEvent outEvent2 = (SearchEvent)outEvents[1];
        assertEquals(event2.query, outEvent2.query);
        assertTrue(outEvent2.hasTag("foo"));

        SearchEvent outEvent3 = (SearchEvent)outEvents[2];
        assertEquals(event3.query, outEvent3.query);

        dumpData("testEventGet: events received back from server:", outEvents);

        // Read back events over REST API and check
        FeedbackEvent getEvent1 = getData(eventApi + "/" + outEvent1.getId(),
                                          FeedbackEvent.class);
        assertEquals(event1.value, getEvent1.value, DELTA);

        Document getDoc = (Document)getEvent1.targettedResource;
        assertEquals(origDoc.uri, getDoc.uri);
        assertEquals(getDoc.getTags().size(), 2);
        assertTrue(getDoc.hasTag("tag1"));
        assertTrue(getDoc.hasTag("tag2"));

        SearchEvent getEvent2 = getData(eventApi + "/" + outEvent2.getId(),
                                        SearchEvent.class);
        assertEquals(event2.query, getEvent2.query);

        SearchEvent getEvent3 = getData(eventApi + "/" + outEvent3.getId(),
                                        SearchEvent.class);
        assertEquals(event3.query, getEvent3.query);

        // Read back uploaded document
        Document getDirectDoc = getData(infoElemApi + "/" + uploadDoc.getId(),
                                        Document.class);

        assertEquals(getDirectDoc.uri, origDoc.uri);

        // Also test accessing an object that doesn't exist
        getDataExpectError(infoElemApi + "/18923742");

        // Also test accessing an object that doesn't exist
        getDataExpectError(eventApi + "/12980942");

        // Test filtering on actor
        Event[] eventsRes = getData(eventsApi + "?actor=TestActor1",
                                    Event[].class);

        assertEquals(2, eventsRes.length);

        for (Event ev : eventsRes) {
            assertEquals(ev.actor, "TestActor1");
        }

        dumpData("events filtered by actor", eventsRes);

        // Test filtering by bad parameters
        getDataExpectError(eventsApi + "?foo=bar");

        // Test filtering on multiple parameters
        SearchEvent[] eventsRes4 = getData(eventsApi + "?query=" + event3.query
                                           + "&actor=TestActor2",
                                           SearchEvent[].class);

        assertEquals(1, eventsRes4.length);

        assertEquals(eventsRes4[0].query, event3.query);

        // Test filtering for information elements
        // InformationElement[] infoElemsRes = getData(infoElemsApi + "?tag=tag1", 
        //                                             InformationElement[].class);

        // assertEquals(1, infoElemsRes.length);

        // for (InformationElement elem : infoElemsRes) {
        //     assertTrue(elem.hasTag("tag1"));
        // }

        // dumpData("info elems filtered by tag", infoElemsRes);
    }

    protected SearchEvent mkSearchEvent(Date start, Date end, double duration) {
        SearchEvent event = new SearchEvent();
        event.query = "dummy search query";
        event.actor = "TestActor";

        if (start != null)
            event.start = start;
        if (end != null)
            event.end = end;
        if (duration >= 0.0)
            event.duration = duration;

        return event;
    }

    /**
       Tests behaviour of start, end and duration
    */
    @Test
    public void testEventTimes() throws Exception {
        Calendar cal = Calendar.getInstance();
        Date end = cal.getTime();
        int dur = 10;
        cal.add(Calendar.SECOND, -dur);
        Date start = cal.getTime();

        SearchEvent[] events = new SearchEvent[5];
        events[0] = mkSearchEvent(start, null, -1.0);
        events[1] = mkSearchEvent(null, end, -1.0);
        events[2] = mkSearchEvent(start, end, -1.0);
        events[3] = mkSearchEvent(start, null, dur);
        events[4] = mkSearchEvent(null, end, dur);

        dumpData("List of events to be uploaded to " + eventsApi, events);

        // Checks to ensure returned object is the same as uploaded
        SearchEvent[] outEvents = uploadEvents(events, SearchEvent[].class);
        assertEquals(events.length, outEvents.length);

        // end should have been set to equal start
        assert(outEvents[0].start.equals(start));
        assert(outEvents[0].end.equals(start));
        assertEquals(outEvents[0].duration, 0.0, DELTA);

        // start should have been set to equal end
        assert(outEvents[1].start.equals(end));
        assert(outEvents[1].end.equals(end));
        assertEquals(outEvents[1].duration, 0.0, DELTA);

        // duration should be set to end-start
        assert(outEvents[2].start.equals(start));
        assert(outEvents[2].end.equals(end));
        assertEquals(outEvents[2].duration, dur, DELTA);

        // should set end as start+duration
        assert(outEvents[3].start.equals(start));
        assert(outEvents[3].end.equals(end));
        assertEquals(outEvents[3].duration, dur, DELTA);

        // should set start to end-duration
        assertTrue(outEvents[4].start + "!=" + start,
                   outEvents[4].start.equals(start));
        assert(outEvents[4].end.equals(end));
        assertEquals(outEvents[4].duration, dur, DELTA);
    }

    @Test
    public void testElemChange() throws Exception {
        String content1 = "foobar";
        String content2 = "hello";
        String content3 = "xyz";
        
        Message msg = createTestEmail(content1, "");
        msg.appId = "iuerhfieruhf";
        msg.addTag("mytag");
        msg.addTag("anothertag");
        MessageEvent event = new MessageEvent();
        event.targettedResource = msg;

        // Upload to DiMe
        MessageEvent outEvent = uploadEvent(event, MessageEvent.class);

        // check that content is still the same
        assertEquals(content1, outEvent.targettedResource.plainTextContent);
        Long msgId = outEvent.targettedResource.getId();


        // copy if from uploaded message
        msg.copyIdFrom(outEvent.targettedResource);

        // change content
        msg.plainTextContent = content2;

        dumpData("Changed message (id)", event);
        
        // Upload the changed message
        MessageEvent outEvent2 = uploadEvent(event, MessageEvent.class);

        // check that content is the changed one
        assertEquals(content2, outEvent2.targettedResource.plainTextContent);
        assertEquals(msgId, outEvent2.targettedResource.getId());

        // Read back infoelement over REST API and check
        Message msg2 = getData(infoElemApi + "/" + msgId, Message.class);

        assertEquals(content2, msg2.plainTextContent);
        assertEquals(2, msg2.getTags().size());
        assertTrue(msg2.hasTag("mytag"));
        assertTrue(msg2.hasTag("anothertag"));


        // Next, try changing using appId instead of id
        msg.resetId();
        msg.plainTextContent = content3;
        assertEquals(msg.getId(), null);

        dumpData("Changed message (appId)", event);

        // Upload the changed message
        MessageEvent outEvent3 = uploadEvent(event, MessageEvent.class);
        
        // check that content is the changed one
        assertEquals(content3, outEvent3.targettedResource.plainTextContent);
        assertEquals(msgId, outEvent3.targettedResource.getId());

        // Read back infoelement over REST API and check
        Message msg3 = getData(infoElemApi + "/" + msgId, Message.class);

        dumpData("Got back", msg3);

        assertEquals(content3, msg3.plainTextContent);
        assertEquals(2, msg3.getTags().size());
        assertTrue(msg3.hasTag("mytag"));
        assertTrue(msg3.hasTag("anothertag"));
    }

    @Test
    public void testEventChange() throws Exception {
        String appId1 = "lk43nguefd";
        String appId2 = "9o543gewlk";

        // Create two events with appIds
        Event[] events = new Event[2];

        String query1 = "some search query";
        String query2 = "some other search";

        SearchEvent searchEvent = new SearchEvent();
        searchEvent.appId = appId1;
        searchEvent.query = query1;
        searchEvent.actor = "TestActor1";
        events[0] = searchEvent;

        String content1 = "foobar";
        String content2 = "barfoo";

        Message msg = createTestEmail(content1, "");
        MessageEvent msgEvent = new MessageEvent();
        msgEvent.appId = appId2;
        msgEvent.targettedResource = msg;
        events[1] = msgEvent;

        // Upload to DiMe
        Event[] outEvents = uploadEvents(events, Event[].class);
        SearchEvent outSearchEvent1 = (SearchEvent)outEvents[0];
        MessageEvent outMsgEvent1 = (MessageEvent)outEvents[1];

        // check that content is still the same
        assertEquals(2, outEvents.length);
        assertEquals(appId1, outSearchEvent1.appId);
        assertEquals(appId2, outMsgEvent1.appId);
        assertEquals(query1, outSearchEvent1.query);
        assertEquals(content1, outMsgEvent1.targettedResource.plainTextContent);


        // Change search event and message content
        searchEvent.query = query2;
        msg.plainTextContent = content2;

        // Upload the changed events
        SearchEvent outSearchEvent2 = uploadEvent(searchEvent, SearchEvent.class);
        MessageEvent outMsgEvent2 = uploadEvent(msgEvent, MessageEvent.class);

        // Sanity check for appIds
        assertEquals(appId1, outSearchEvent2.appId);
        assertEquals(msgEvent.appId, outMsgEvent2.appId);

        // check that content is the changed one
        assertEquals(query2, outSearchEvent2.query);
        assertEquals(content2, outMsgEvent2.targettedResource.plainTextContent);


        // Read back events over REST API and check again
        SearchEvent[] searchEventGot = getData(eventsApi + "?appid=" + appId1,
                                               SearchEvent[].class);

        MessageEvent[] msgEventGot = getData(eventsApi + "?appid=" + appId2,
                                             MessageEvent[].class);

        MessageEvent[] msgEventGot2 = getData(eventsApi + 
                                              "?includePlainTextContent=true&appid=" 
                                              + appId2, MessageEvent[].class);

        // Sanity check for appIds
        assertEquals(appId1, searchEventGot[0].appId);
        assertEquals(appId2, msgEventGot[0].appId);
        assertEquals(appId2, msgEventGot2[0].appId);

        // check that content is the changed one
        assertEquals(query2, searchEventGot[0].query);
        assertEquals(null, msgEventGot[0].targettedResource.plainTextContent);
        assertEquals(content2, msgEventGot2[0].targettedResource.plainTextContent);
    }

    @Test
    public void testElemUpload() throws Exception {
        String content1 = "foobar";
        String content2 = "barfoo";
        String content3 = "appIdfoo";
        Message msg = createTestEmail(content1, "");
        msg.appId = "hfpiewhfi";

        // Upload to DiMe
        Message outMsg = uploadElement(msg, Message.class);

        // check that content is still the same
        assertEquals(outMsg.plainTextContent, content1);
        Long msgId = outMsg.getId();

        // Read back infoelement over REST API and check
        Message msg2 = getData(infoElemApi + "/" + msgId, Message.class);

        assertEquals(msg2.plainTextContent, content1);

        // Copy id from uploaded msg and change content
        msg.copyIdFrom(outMsg);
        msg.plainTextContent = content2;

        // Upload to DiMe
        Message outMsg2 = uploadElement(msg, Message.class);

        // check that content is the new one
        assertEquals(content2, outMsg2.plainTextContent);
        assertEquals(msgId, outMsg2.getId());

        // Read back infoelement over REST API and check
        Message msg3 = getData(infoElemApi + "/" + msgId, Message.class);

        assertEquals(msg3.plainTextContent, content2);


        // Reset id and try appId instead
        msg.resetId();
        msg.plainTextContent = content3;

        // Upload to DiMe
        Message outMsg3 = uploadElement(msg, Message.class);

        // check that content is the new one
        assertEquals(content3, outMsg3.plainTextContent);
        assertEquals(msgId, outMsg3.getId());
        assertEquals(msg.appId, outMsg3.appId);

        // Read back infoelement over REST API and check
        Message msg4 = getData(infoElemApi + "/" + msgId, Message.class);

        assertEquals(msg4.plainTextContent, content3);


        // Finally, read back infoelement with appId
        Message[] msgs = getData(infoElemsApi + "?appid=" + msg.appId, Message[].class);

        assertEquals(1, msgs.length);
        assertEquals(content3, msgs[0].plainTextContent);
        assertEquals(msg.to.size(), msgs[0].to.size());
        assertEquals(msg.cc.size(), msgs[0].cc.size());
    }

    @Test
    public void testCustomId() throws Exception {
        class FakeEvent {
            public Long id;
            public String query;
            
            @JsonProperty("@type")
            public String type = "SearchEvent";
        }
        
        FakeEvent event = new FakeEvent();
        event.id = 12903812L;
        event.query = "hello";

        dumpData("Uploading fake id", event);
        
        // Upload to DiMe
        ApiError res = uploadData(eventApi, event, ApiError.class);
        
        System.out.println("RES=" + res);
    }

    @Test
    public void testReadingEvent() throws Exception {
        ScientificDocument doc = createScientificDocument(randomText);

        ReadingEvent re =
            createReadingEvent(doc, doc.plainTextContent.substring(25,150));

        dumpData("ReadingEvent before", re);

        ReadingEvent reRet = uploadEvent(re, ReadingEvent.class);
        
        dumpData("ReadingEvent back", reRet);

        assertEquals(re.pageEyeData.size(), reRet.pageEyeData.size());
        assertEquals(re.pageRects.size(), reRet.pageRects.size());

        ReadingEvent reGet = getData(eventApi + "/" + reRet.getId(),
                                     ReadingEvent.class);
        dumpData("ReadingEvent via GET", reGet);

        assertEquals(re.pageEyeData.size(), reGet.pageEyeData.size());
        assertEquals(re.pageRects.size(), reGet.pageRects.size());

        ScientificDocument docGet = (ScientificDocument)reGet.targettedResource;
        assertEquals(doc.authors.size(), docGet.authors.size());

        SummaryReadingEvent sre = new SummaryReadingEvent();
        fillReadingEvent(sre, doc, doc.plainTextContent.substring(25,150));
        sre.proportionRead = 0.432;
        sre.proportionInteresting = 0.123;
        sre.proportionCritical = 0.052;
        sre.foundStrings = new ArrayList<String>();
        sre.foundStrings.add("foo");
        sre.foundStrings.add("bar");

        SummaryReadingEvent sreRet =
            uploadEvent(sre, SummaryReadingEvent.class);
        dumpData("SummaryReadingEvent", sreRet);
    }

    protected void compareDocs(ScientificDocument doc1, ScientificDocument doc2) {
        assertEquals(doc1.appId, doc2.appId);
        assertEquals(doc1.plainTextContent, doc2.plainTextContent);
        assertEquals(doc1.title, doc2.title);
        assertEquals(doc1.authors.size(), doc2.authors.size());
        for (int i=0; i<doc1.authors.size(); i++) {
            Person a1 = doc1.authors.get(i);
            Person a2 = doc2.authors.get(i);
            assertEquals(a1.firstName, a2.firstName);
            assertEquals(a1.lastName, a2.lastName);
            assertEquals(a1.middleNames.size(), a2.middleNames.size());
            for (int j=0; j<a1.middleNames.size(); j++)
                assertEquals(a1.middleNames.get(j), a2.middleNames.get(j));
        }

        assertEquals(doc1.keywords.size(), doc2.keywords.size());
        assertEquals(doc1.keywords.get(0),
                     doc2.keywords.get(0));
    }

    @Test
    public void testScientificDocument() throws Exception {
        ScientificDocument doc = createScientificDocument(randomText);
        doc.appId = "oiuhgferiufheroi";
        assertTrue(doc.authors.size() > 0);
        assertTrue(doc.keywords.size() > 0);

        dumpData("ScientificDocument before", doc);

        ScientificDocument docRet = uploadElement(doc, ScientificDocument.class);
        dumpData("ScientificDocument after", docRet);
        compareDocs(doc, docRet);


        ScientificDocument docGet = getData(infoElemApi + "/" + docRet.getId(), 
                                            ScientificDocument.class);
        dumpData("ScientificDocument GET id", docGet);
        compareDocs(doc, docGet);


        ScientificDocument[] docGet2 = getData(infoElemsApi + "?appId=" + doc.appId, 
                                              ScientificDocument[].class);
        assertEquals(1, docGet2.length);
        dumpData("ScientificDocument GET appId", docGet2[0]);

        compareDocs(doc, docGet2[0]);
    }

    @Test
    public void testUpdateWithSubclass() throws Exception {
       ScientificDocument docSub = createScientificDocument(randomText);
       docSub.appId = "oweigjeroijgo";

       Document docSup = new Document();
       docSup.uri = docSub.uri;
       docSup.plainTextContent = docSub.plainTextContent;
       docSup.mimeType = docSub.mimeType;
        docSup.appId = docSub.appId;

        docSub.plainTextContent += "some addition";

        // First, upload superclass to DiMe
        Document resSup = uploadElement(docSup, Document.class);
        dumpData("testUpdateWithSubclass: docSup", resSup);
        
       // Second, try update with subclass and expect error
        ApiError resSub = uploadData(infoElemApi, docSub, ApiError.class);
        dumpData("testUpdateWithSubclass: docSub", resSub);
    }

    @Test
    public void testUpdateWithSuperclass() throws Exception {
        ScientificDocument docSub = createScientificDocument(randomText);
        docSub.appId = "wroifjoij";

        Document docSup = new Document();
        docSup.uri = docSub.uri;
        docSup.plainTextContent = docSub.plainTextContent + "some addition";
        docSup.mimeType = docSub.mimeType;
        docSup.appId = docSub.appId;

        // First, upload subclass to DiMe
        ScientificDocument resSub = uploadElement(docSub,
                                                  ScientificDocument.class);
        dumpData("testUpdateWithSuperclass: docSub", resSub);

        // Second, try update with superclass and expect error
        ApiError resSup = uploadData(infoElemApi, docSup, ApiError.class);
        dumpData("testUpdateWithSuperclass: docSup", resSup);
    }

    @Test
    public void testNewTags() throws Exception {
        Document doc = new Document();
        doc.plainTextContent = "foobar";
        doc.addTag("foo");
        doc.addTag("bar");
        doc.addTag("baz");

        Tag tagFoo = new Tag("foo");
        tagFoo.auto = true;
        doc.addTag(tagFoo);

        doc.removeTag("baz");

        assertEquals(doc.getTags().size(), 2);
        assertTrue(doc.hasTag("foo"));
        assertTrue(doc.hasTag("bar"));
        assertFalse(doc.hasTag("baz"));
        assertTrue(doc.getTag("foo").auto);

        FeedbackEvent event = new FeedbackEvent();
        event.value = 0.42;
        event.targettedResource = doc;

        dumpData("Event with tagged doc to be uploaded", event);

        FeedbackEvent outEvent = uploadEvent(event, FeedbackEvent.class);
        dumpData("Event received back from server:", outEvent);

        Document getDoc = getData(infoElemApi + "/" +
                                  outEvent.targettedResource.getId(),
                                  Document.class);
        dumpData("Tagged doc fetched:", getDoc);

        assertEquals(2, getDoc.getTags().size());
        assertTrue(getDoc.hasTag("foo"));
        assertTrue(getDoc.hasTag("bar"));
        assertFalse(getDoc.hasTag("baz"));

        assertTrue(getDoc.getTag("foo").auto);
        assertFalse(getDoc.getTag("bar").auto);

        // ApiError res = uploadData(eventApi, event, ApiError.class);
        // System.out.println("RES=" + res);

    }
}
