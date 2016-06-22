/*
  Copyright (c) 2015-2016 University of Helsinki

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
import static fi.hiit.dime.data.DiMeData.makeStub;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import static org.junit.Assert.*;
import static org.hamcrest.CoreMatchers.*;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
        InformationElement stubDoc = makeStub(outDoc1, InformationElement.class);

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
            getData(eventsApi + "?elemId=" + outDoc1.getId(), 
                    FeedbackEvent[].class);
        
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
        FeedbackEvent getEvent1 = getEvent(outEvent1.getId(),
                                           FeedbackEvent.class);
        assertEquals(event1.value, getEvent1.value, DELTA);

        Document getDoc = (Document)getEvent1.targettedResource;
        assertEquals(origDoc.uri, getDoc.uri);
        assertEquals(getDoc.getTags().size(), 2);
        assertTrue(getDoc.hasTag("tag1"));
        assertTrue(getDoc.hasTag("tag2"));

        SearchEvent getEvent2 = getEvent(outEvent2.getId(), SearchEvent.class);
        assertEquals(event2.query, getEvent2.query);

        SearchEvent getEvent3 = getEvent(outEvent3.getId(), SearchEvent.class);
        assertEquals(event3.query, getEvent3.query);

        // Read back uploaded document
        Document getDirectDoc = getElement(uploadDoc.getId(), Document.class);

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
        InformationElement[] infoElemsRes = getData(infoElemsApi + "?tag=tag1", 
                                                    InformationElement[].class);

        assertEquals(1, infoElemsRes.length);

        for (InformationElement elem : infoElemsRes) {
            assertTrue(elem.hasTag("tag1"));
        }

        dumpData("info elems filtered by tag", infoElemsRes);
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

        dumpData("testEventTimes: List of events to be uploaded to " + eventsApi, events);

        // Checks to ensure returned object is the same as uploaded
        SearchEvent[] outEvents = uploadEvents(events, SearchEvent[].class);
        assertEquals(events.length, outEvents.length);

        dumpData("testEventTimes: List of events after upload", outEvents);

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

        // test updating an old event with new times
        cal.add(Calendar.HOUR, -24);
        Date start2 = cal.getTime(); // set start time one day back
        double dur2 = (end.getTime()-start2.getTime())/1000.0;

        events[2].copyIdFrom(outEvents[2]); // use the id returned by DiMe
        events[2].start = start2;

        SearchEvent uploadedEvent = uploadEvent(events[2], SearchEvent.class);
        dumpData("Modified times event", uploadedEvent);

        assert(uploadedEvent.start.equals(start2));
        assert(uploadedEvent.end.equals(end));
        assertEquals(dur2, uploadedEvent.duration, DELTA);
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
        Message msg2 = getElement(msgId, Message.class);

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
        Message msg3 = getElement(msgId, Message.class);

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
        Message msg2 = getElement(msgId, Message.class);

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
        Message msg3 = getElement(msgId, Message.class);

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
        Message msg4 = getElement(msgId, Message.class);

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

        ReadingEvent reGet = getEvent(reRet.getId(), ReadingEvent.class);
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


        ScientificDocument docGet = getElement(docRet.getId(),
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

        Document getDoc = getElement(outEvent.targettedResource.getId(),
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

    @Test
    public void testTagAPI() throws Exception {
        Document doc = new Document();
        doc.plainTextContent = "foobar";

        Document uploadedDoc = uploadElement(doc, Document.class);
        assertFalse(uploadedDoc.hasTags());

        long docId = uploadedDoc.getId();

        Tag tag1 = new Tag("foo", true);

        Document uploadedDoc2 =
            uploadData(apiUrl("/data/informationelement/" + docId + "/addtag"),
                       tag1, Document.class);
        assertEquals(1, uploadedDoc2.getTags().size());
        assertTrue(uploadedDoc2.hasTag("foo"));
        assertTrue(uploadedDoc2.getTag("foo").auto);

        Document getDoc1 = getElement(docId, Document.class);
        assertEquals(1, getDoc1.getTags().size());
        assertTrue(getDoc1.hasTag("foo"));
        assertTrue(getDoc1.getTag("foo").auto);

        Tag[] tags = new Tag[2];
        tags[0] = new Tag("bar", true);
        tags[1] = new Tag("baz", false);

        Document uploadedDoc3 =
            uploadData(apiUrl("/data/informationelement/" + docId + "/addtags"),
                       tags, Document.class);
        assertEquals(3, uploadedDoc3.getTags().size());
        assertTrue(uploadedDoc3.hasTag("foo"));
        assertTrue(uploadedDoc3.hasTag("bar"));
        assertTrue(uploadedDoc3.hasTag("baz"));
        assertFalse(uploadedDoc3.hasTag("something_else"));
        assertTrue(uploadedDoc3.getTag("foo").auto);
        assertTrue(uploadedDoc3.getTag("bar").auto);
        assertFalse(uploadedDoc3.getTag("baz").auto);

        Document getDoc2 = getElement(docId, Document.class);
        assertEquals(3, getDoc2.getTags().size());
        assertTrue(getDoc2.hasTag("foo"));
        assertTrue(getDoc2.hasTag("bar"));
        assertTrue(getDoc2.hasTag("baz"));
        assertTrue(getDoc2.getTag("foo").auto);
        assertTrue(getDoc2.getTag("bar").auto);
        assertFalse(getDoc2.getTag("baz").auto);

        Document uploadedDoc4 =
            uploadData(apiUrl("/data/informationelement/" + docId + "/removetag"),
                       new Tag("bar"), Document.class);
        assertEquals(2, uploadedDoc4.getTags().size());
        assertTrue(uploadedDoc4.hasTag("foo"));
        assertFalse(uploadedDoc4.hasTag("bar"));
        assertTrue(uploadedDoc4.hasTag("baz"));

        Document getDoc3 = getElement(docId, Document.class);
        assertEquals(2, getDoc3.getTags().size());
        assertTrue(getDoc3.hasTag("foo"));
        assertFalse(getDoc3.hasTag("bar"));
        assertTrue(getDoc3.hasTag("baz"));
    }    

    @Test
    public void testTagAPIEvents() throws Exception {
        SearchEvent event = new SearchEvent();
        event.query = "foobar";

        SearchEvent uploadedEvent = uploadEvent(event, SearchEvent.class);
        assertFalse(uploadedEvent.hasTags());

        long eventId = uploadedEvent.getId();

        Tag tag1 = new Tag("foo", true);

        SearchEvent uploadedEvent2 =
            uploadData(apiUrl("/data/event/" + eventId + "/addtag"),
                       tag1, SearchEvent.class);
        assertEquals(1, uploadedEvent2.getTags().size());
        assertTrue(uploadedEvent2.hasTag("foo"));
        assertTrue(uploadedEvent2.getTag("foo").auto);

        SearchEvent getEvent1 = getEvent(eventId, SearchEvent.class);
        assertEquals(1, getEvent1.getTags().size());
        assertTrue(getEvent1.hasTag("foo"));
        assertTrue(getEvent1.getTag("foo").auto);

        Tag[] tags = new Tag[2];
        tags[0] = new Tag("bar", true);
        tags[1] = new Tag("baz", false);

        SearchEvent uploadedEvent3 =
            uploadData(apiUrl("/data/event/" + eventId + "/addtags"),
                       tags, SearchEvent.class);
        assertEquals(3, uploadedEvent3.getTags().size());
        assertTrue(uploadedEvent3.hasTag("foo"));
        assertTrue(uploadedEvent3.hasTag("bar"));
        assertTrue(uploadedEvent3.hasTag("baz"));
        assertFalse(uploadedEvent3.hasTag("something_else"));
        assertTrue(uploadedEvent3.getTag("foo").auto);
        assertTrue(uploadedEvent3.getTag("bar").auto);
        assertFalse(uploadedEvent3.getTag("baz").auto);

        SearchEvent getEvent2 = getEvent(eventId, SearchEvent.class);
        assertEquals(3, getEvent2.getTags().size());
        assertTrue(getEvent2.hasTag("foo"));
        assertTrue(getEvent2.hasTag("bar"));
        assertTrue(getEvent2.hasTag("baz"));
        assertTrue(getEvent2.getTag("foo").auto);
        assertTrue(getEvent2.getTag("bar").auto);
        assertFalse(getEvent2.getTag("baz").auto);

        SearchEvent uploadedEvent4 =
            uploadData(apiUrl("/data/event/" + eventId + "/removetag"),
                       new Tag("foo"), SearchEvent.class);
        assertEquals(2, uploadedEvent4.getTags().size());
        assertFalse(uploadedEvent4.hasTag("foo"));
        assertTrue(uploadedEvent4.hasTag("bar"));
        assertTrue(uploadedEvent4.hasTag("baz"));

        SearchEvent getEvent3 = getEvent(eventId, SearchEvent.class);
        assertEquals(2, getEvent3.getTags().size());
        assertFalse(getEvent3.hasTag("foo"));
        assertTrue(getEvent3.hasTag("bar"));
        assertTrue(getEvent3.hasTag("baz"));
    }    

    protected FeedbackEvent mkFeedback(double value, InformationElement elem, 
                                       Event relatedEvent) {
        FeedbackEvent feedback = new FeedbackEvent();
        feedback.value = value;
        if (elem != null)
            feedback.targettedResource = elem;
        if (relatedEvent != null)
            feedback.relatedEvent = relatedEvent;
        return feedback;
    }
        

    @Test
    public void testRelatedEvent() throws Exception {
        // Let's pretend we searched for something
        SearchEvent searchEvent = new SearchEvent();
        searchEvent.query = "some search query";

        SearchEvent searchEventOut = uploadEvent(searchEvent, SearchEvent.class);

        // Let's pretend we found two documents
        Document doc1 = new Document();
        doc1.uri = "http://www.example.com/hello.txt";
        doc1.plainTextContent = "Hello, world";
        doc1.mimeType = "text/plain";

        Document doc2 = new Document();
        doc2.uri = "http://www.example.com/hello2.txt";
        doc2.plainTextContent = "Hello, world too";
        doc2.mimeType = "text/plain";
        
        // Then the user gave some feedback
        FeedbackEvent[] feedback = new FeedbackEvent[5];
        feedback[0] = mkFeedback(0.287, doc1, searchEventOut);
        feedback[1] = mkFeedback(0.984, doc1, searchEventOut);
        feedback[2] = mkFeedback(0.398, doc2, searchEventOut);
        feedback[3] = mkFeedback(0.402, doc2, searchEventOut);

        SearchEvent stubSearchEvent = makeStub(searchEventOut, SearchEvent.class);
        feedback[4] = mkFeedback(0.234, doc2, stubSearchEvent);

        dumpData("testRelatedEvent: feedback to be uploaded ", feedback);

        FeedbackEvent[] feedbackOut = uploadEvents(feedback, FeedbackEvent[].class);

        dumpData("testRelatedEvent: feedback that was returned ", feedbackOut);

        for (int i=0; i<feedback.length; i++) {
            FeedbackEvent in = feedback[i];
            FeedbackEvent out = feedbackOut[i];
            assertEquals(in.value, out.value);
            assertEquals(in.targettedResource.uri, out.targettedResource.uri);

            assertTrue(out.relatedEvent instanceof SearchEvent);
            SearchEvent relatedOut = (SearchEvent)out.relatedEvent;
            assertEquals(searchEventOut.getId(), relatedOut.getId());
            //assertEquals(searchEvent.query, relatedOut.query);
        }

        SearchEvent getSearchEvent = getEvent(searchEventOut.getId(),
                                              SearchEvent.class);
        dumpData("testRelatedEvent: searchEvent got back", getSearchEvent);

        assertEquals(searchEvent.query, getSearchEvent.query);

    }

    @Test
    public void testEventTimeFiltering() throws Exception {
        final int n = 5;

        // Generate n timestamps 10 minutes apart, starting from one
        // hour ago, and SearchEvents at those times
        Calendar cal = Calendar.getInstance();
        cal.add(Calendar.HOUR, -1);

        SearchEvent[] events = new SearchEvent[n];
        Date[] date = new Date[5];

        for (int i=0; i<n; i++) {
            date[i] = cal.getTime();
            events[i] = mkSearchEvent(date[i], null, 10.0);

            cal.add(Calendar.MINUTE, 5);
        }

        dumpData("testEventTimeFiltering: List of events to be uploaded", events);

        SearchEvent[] eventsOut = uploadEvents(events, SearchEvent[].class);

        assertEquals(n, eventsOut.length);

        // Try filtering events after
        String afterParam1 = "?after=" + date[2].getTime();
        System.out.println("testEventTimeFiltering: " + afterParam1);

        SearchEvent[] eventsAfter1 = getData(eventsApi + afterParam1,
            SearchEvent[].class);
        assertEquals(3, eventsAfter1.length);

        // Try with empty set
        cal.add(Calendar.MINUTE, 1);
        
        String afterParam2 = "?after=" + cal.getTime().getTime();
        System.out.println("testEventTimeFiltering: " + afterParam2);

        SearchEvent[] eventsAfter2 = getData(eventsApi + afterParam2,
            SearchEvent[].class);
        assertEquals(0, eventsAfter2.length);

        // Try with human readable timestamp
        SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssZ");

        String afterParam3 = "?after=" + df.format(date[3]);
        System.out.println("testEventTimeFiltering: " + afterParam3);

        SearchEvent[] eventsAfter3 = getData(eventsApi + afterParam3,
            SearchEvent[].class);
        assertEquals(2, eventsAfter3.length);

        // Try filtering events before
        String beforeParam1 = "?before=" + date[2].getTime();
        System.out.println("testEventTimeFiltering: " + beforeParam1);

        SearchEvent[] eventsBefore1 = getData(eventsApi + beforeParam1,
            SearchEvent[].class);
        assertEquals(2, eventsBefore1.length);
        
        // Try filtering events between
        String betweenParam1 = "?after=" + date[1].getTime() + "&before=" +
            date[3].getTime();
        System.out.println("testEventTimeFiltering: " + betweenParam1);

        SearchEvent[] eventsBetween1 = getData(eventsApi + betweenParam1,
            SearchEvent[].class);
        assertEquals(2, eventsBetween1.length);

        // Try between with after > before -> should get empty set
        String betweenParam2 = "?after=" + date[2].getTime() + "&before=" +
            date[1].getTime();
        System.out.println("testEventTimeFiltering: " + betweenParam2);

        SearchEvent[] eventsBetween2 = getData(eventsApi + betweenParam2,
            SearchEvent[].class);
        assertEquals(0, eventsBetween2.length);
        
    }

    @Test
    public void testIntentModelEvent() throws Exception {
        IntentModelEvent event = new IntentModelEvent();
        event.model = new HashMap<String, Double>();
        event.model.put("foo", 0.29);
        event.model.put("bar", 0.48);
        event.model.put("baz", 0.19);

        IntentModelEvent uploadEvent = uploadEvent(event, 
                                                   IntentModelEvent.class);
        
        IntentModelEvent getEvent = getEvent(uploadEvent.getId(), 
                                             IntentModelEvent.class);

        assertEquals(event.model.size(), getEvent.model.size());

        for (Map.Entry<String, Double> it : event.model.entrySet()) {
            String word = it.getKey();
            Double weight = it.getValue();
            assertTrue(getEvent.model.containsKey(word));
            assertEquals(weight, getEvent.model.get(word));
        }
    }

    @Test
    public void testEventDelete() throws Exception {
        SearchEvent event = new SearchEvent();
        event.query = "some search query";

        SearchEvent uploadedEvent = uploadEvent(event, SearchEvent.class);
        long id = uploadedEvent.getId();

        // try GET, expect success
        SearchEvent getBeforeEvent = getEvent(id, SearchEvent.class);

        String eventApiUrl = eventApi + "/" + id;
        
        System.out.println("testEventDelete");
        // DELETE uploadedEvent.id
        deleteData(eventApiUrl);

        // try GET, expect failure
        ApiError error = getDataExpectError(eventApiUrl);
    }

    @Test
    public void testResourcedEventDelete() throws Exception {
        Document doc = new Document();
        doc.plainTextContent = "foobar";

        FeedbackEvent event1 = new FeedbackEvent();
        event1.value = 0.42;
        event1.targettedResource = doc;

        FeedbackEvent uploadedEvent1 = uploadEvent(event1, FeedbackEvent.class);
        long event1Id = uploadedEvent1.getId();
        Long elemId = uploadedEvent1.targettedResource.getId();

        // Add another event referring to the same document
        FeedbackEvent event2 = new FeedbackEvent();
        event2.value = 0.68;
        event2.targettedResource = uploadedEvent1.targettedResource;

        FeedbackEvent uploadedEvent2 = uploadEvent(event2, FeedbackEvent.class);
        long event2Id = uploadedEvent2.getId();
        assertEquals(elemId, uploadedEvent2.targettedResource.getId());

        // try GET, expect success
        FeedbackEvent getBeforeEvent1 = getEvent(event1Id, FeedbackEvent.class);
        FeedbackEvent getBeforeEvent2 = getEvent(event2Id, FeedbackEvent.class);

        getElement(elemId, Document.class);

        System.out.println("testResourcedEventDelete");
        deleteData(eventApi + "/" + event1Id);

        // try GET, expect failure for event1 only
        getDataExpectError(eventApi + "/" + event1Id);
        getEvent(event2Id, FeedbackEvent.class);

        //ApiError error2 = getDataExpectError(infoElemApi + "/" + elemId);
        getElement(elemId, Document.class);

        deleteData(eventApi + "/" + event2Id);

        // try GET, expect failure for both events
        getDataExpectError(eventApi + "/" + event1Id);
        getDataExpectError(eventApi + "/" + event2Id);

        // Expect orphan element to still be there
        getElement(elemId, Document.class);
    }

    @Test
    public void testElementDelete() throws Exception {
        Document doc = new Document();
        doc.plainTextContent = "foobar";

        FeedbackEvent event1 = new FeedbackEvent();
        event1.value = 0.42;
        event1.targettedResource = doc;

        FeedbackEvent uploadedEvent1 = uploadEvent(event1, FeedbackEvent.class);
        long event1Id = uploadedEvent1.getId();
        Long elemId = uploadedEvent1.targettedResource.getId();

        // Add another event referring to the same document
        FeedbackEvent event2 = new FeedbackEvent();
        event2.value = 0.68;
        event2.targettedResource = uploadedEvent1.targettedResource;

        FeedbackEvent uploadedEvent2 = uploadEvent(event2, FeedbackEvent.class);
        long event2Id = uploadedEvent2.getId();
        assertEquals(elemId, uploadedEvent2.targettedResource.getId());

        // try GET, expect success
        getEvent(event1Id, FeedbackEvent.class);
        getEvent(event2Id, FeedbackEvent.class);

        getElement(elemId, Document.class);

        System.out.println("testElementDelete");
        deleteData(infoElemApi + "/" + elemId);

        // try GET, expect failure for all, since deleting element
        // should delete also all its events
        getDataExpectError(eventApi + "/" + event1Id);
        getDataExpectError(eventApi + "/" + event2Id);
        getDataExpectError(infoElemApi + "/" + elemId);
    }

}
