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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.List;


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
	
	SearchEvent outEvent3 = (SearchEvent)outEvents[2];
	assertEquals(event3.query, outEvent3.query);

	dumpData("testEventGet: events received back from server:", outEvents);

	// Read back events over REST API and check
	FeedbackEvent getEvent1 = getData(eventApi + "/" + outEvent1.getId(),
					  FeedbackEvent.class);
	assertEquals(event1.value, getEvent1.value, DELTA);

	Document getDoc = (Document)getEvent1.targettedResource;
	assertEquals(origDoc.uri, getDoc.uri);
	assertEquals(getDoc.tags.size(), 2);
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
	assertEquals(2, msg2.tags.size());
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
	assertEquals(2, msg3.tags.size());
	assertTrue(msg3.hasTag("mytag"));
	assertTrue(msg3.hasTag("anothertag"));
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
	Message[] msgs = getData(infoElemsApi + "?appId=" + msg.appId, Message[].class);

	assertEquals(1, msgs.length);
	assertEquals(content3, msgs[0].plainTextContent);

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
	String res = uploadData(eventApi, event, String.class, true);
	
	System.out.println("RES=" + res);
    }

    @Test
    public void testReadingEvent() throws Exception {
	String someText = "Aliquam erat volutpat.  Nunc eleifend leo vitae magna.  In id erat non orci commodo lobortis.  Proin neque massa, cursus ut, gravida ut, lobortis eget, lacus.  Sed diam.  Praesent fermentum tempor tellus.  Nullam tempus.  Mauris ac felis vel velit tristique imperdiet.  Donec at pede.  Etiam vel neque nec dui dignissim bibendum.  Vivamus id enim.  Phasellus neque orci, porta a, aliquet quis, semper a, massa.  Phasellus purus.  Pellentesque tristique imperdiet tortor.  Nam euismod tellus id erat.";

	ReadingEvent re = new ReadingEvent();
	re.type = "http://www.hiit.fi/ontologies/dime/#ReadingEvent";
	re.plainTextContent = someText.substring(25,150);
	re.foundStrings = Arrays.asList("aliquam", "volutpat", "tellus");
	re.pageNumbers = Arrays.asList(0, 4);

	List<PageEyeData> eyeData = new ArrayList<PageEyeData>();
	for (int i=0; i<10; i++) {
	    PageEyeData ed = new PageEyeData();
	    ed.Xs = Arrays.asList(i*0.0, i*1.5, i*2.2);
	    ed.Ys = Arrays.asList(i*0.0, i*1.5, i*2.2);
	    ed.Ps = Arrays.asList(i*0.0, i*1.5, i*2.2);

	    ed.startTimes = Arrays.asList(i*1l, i*2l, i*4l);
	    ed.endTimes = Arrays.asList(i+1l, i*2+1l, i*4+2l);

	    ed.durations = Arrays.asList(1l, 1l, 2l);

	    ed.pageIndex = i;
	    eyeData.add(ed);
	}

	re.pageEyeData = eyeData;

	List<Rect> rs = new ArrayList<Rect>();
	Rect r = new Rect();
	r.origin = new Point(0.0, 453.5);
	r.readingClass = Rect.CLASS_VIEWPORT;
	r.pageIndex = 0;
	r.classSource = 1;
	r.size = new Size(612.0, 338.5);
	rs.add(r);
	re.pageRects = rs;

	re.scaleFactor = 1.685;
	
	ScientificDocument doc = new ScientificDocument();
	doc.mimeType = "application/pdf";
	doc.title = "Microsoft Word - paper.docx";
	doc.plainTextContent = someText;
	doc.uri = "/home/testuser/docs/memex_iui2016_submittedversion.pdf";
	doc.firstPage = 0;
	doc.lastPage = 0;
	doc.year = 0;
	doc.type = "http://www.hiit.fi/ontologies/dime/#ScientificDocument";
	
	re.targettedResource = doc;

	dumpData("ReadingEvent before", re);

	ReadingEvent reRet = uploadEvent(re, ReadingEvent.class);
	
	dumpData("ReadingEvent back", reRet);

    	// ResponseEntity<String> ress = getRest().postForEntity(eventApi, re, 
	// 						      String.class);

	// // String res = uploadData(eventApi, re, String.class, true);
	// String res = ress.getBody();
	// System.out.println("RES=" + res);
    }

}
