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

	// Upload to DiMe
	ResponseEntity<FeedbackEvent> res1 = 
	    getRest().postForEntity(eventApi, event1, FeedbackEvent.class);

	// Check that HTTP was successful
	assertSuccessful(res1);

	// Checks to ensure returned object is the same as uploaded
	FeedbackEvent outEvent1 = res1.getBody();
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
	
	ResponseEntity<FeedbackEvent> res2 = 
	    getRest().postForEntity(eventApi, event2, FeedbackEvent.class);

	// Check that HTTP was successful
	assertSuccessful(res2);

	// Checks to ensure returned object is the same as uploaded
	FeedbackEvent outEvent2 = res2.getBody();
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
	
	ResponseEntity<FeedbackEvent> res3 = 
	    getRest().postForEntity(eventApi, event3, FeedbackEvent.class);

	// Check that HTTP was successful
	assertSuccessful(res3);

	// Checks to ensure returned object is the same as uploaded
	FeedbackEvent outEvent3 = res3.getBody();
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

	// Upload to DiMe
	ResponseEntity<MessageEvent> res1 = 
	    getRest().postForEntity(eventApi, event1, MessageEvent.class);
	
	// Check that HTTP was successful
	assertSuccessful(res1);

	// Checks to ensure returned object is the same as uploaded
	MessageEvent outEvent1 = res1.getBody();
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

	// Upload to DiMe
	ResponseEntity<Event[]> uploadRes = 
	    getRest().postForEntity(eventsApi, events, Event[].class);

	// Check that HTTP was successful
	assertSuccessful(uploadRes);

	// Checks to ensure returned object is the same as uploaded
	Event[] outEvents = uploadRes.getBody();
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
	ResponseEntity<FeedbackEvent> getRes1 = 
	    getRest().getForEntity(eventApi + "/" + outEvent1.getId(),
				   FeedbackEvent.class);
	assertSuccessful(getRes1);

	FeedbackEvent getEvent1 = getRes1.getBody();
	assertEquals(event1.value, getEvent1.value, DELTA);

	Document getDoc = (Document)getEvent1.targettedResource;
	assertEquals(origDoc.uri, getDoc.uri);
	assertEquals(getDoc.tags.size(), 2);
	assertTrue(getDoc.hasTag("tag1"));
	assertTrue(getDoc.hasTag("tag2"));

	ResponseEntity<SearchEvent> getRes2 = 
	    getRest().getForEntity(eventApi + "/" + outEvent2.getId(),
				   SearchEvent.class);

	SearchEvent getEvent2 = getRes2.getBody();
	assertEquals(event2.query, getEvent2.query);

	ResponseEntity<SearchEvent> getRes3 = 
	    getRest().getForEntity(eventApi + "/" + outEvent3.getId(),
				   SearchEvent.class);

	SearchEvent getEvent3 = getRes3.getBody();
	assertEquals(event3.query, getEvent3.query);

	// Read back uploaded document
	ResponseEntity<Document> getDocRes = 
	    getRest().getForEntity(infoElemApi + "/" + uploadDoc.getId(),
				   Document.class);
	assertSuccessful(getDocRes);

	Document getDirectDoc = getDocRes.getBody();
	assertEquals(getDirectDoc.uri, origDoc.uri);

	// Also test accessing an object that doesn't exist
	ResponseEntity<Document> getBadRes1 = 
	    getRest().getForEntity(infoElemApi + "/18923742",
				   Document.class);
	assertClientError(getBadRes1);

	// Also test accessing an object that doesn't exist
	ResponseEntity<SearchEvent> getBadRes2 = 
	    getRest().getForEntity(eventApi + "/12980942",
				   SearchEvent.class);
	assertClientError(getBadRes2);

	// Test filtering on actor
	ResponseEntity<Event[]> getEventsRes = 
	    getRest().getForEntity(eventsApi + "?actor=TestActor1",
				   Event[].class);
	assertSuccessful(getEventsRes);

	Event[] eventsRes = getEventsRes.getBody();
	assertEquals(2, eventsRes.length);

	for (Event ev : eventsRes) {
	    assertEquals(ev.actor, "TestActor1");
	}

	dumpData("events filtered by actor", eventsRes);

	// Test filtering by bad parameters
	ResponseEntity<Event[]> getEventsRes3 = 
	    getRest().getForEntity(eventsApi + "?foo=bar",
				   Event[].class);
	assertClientError(getEventsRes3);

	// Test filtering on multiple parameters
	ResponseEntity<SearchEvent[]> getEventsRes4 = 
	    getRest().getForEntity(eventsApi + "?query=" + event3.query
				   + "&actor=TestActor2",
				   SearchEvent[].class);
	assertSuccessful(getEventsRes4);

	SearchEvent[] eventsRes4 = getEventsRes4.getBody();
	assertEquals(1, eventsRes4.length);

	assertEquals(eventsRes4[0].query, event3.query);

	// Test filtering for information elements
	ResponseEntity<InformationElement[]> getInfoElems = 
	    getRest().getForEntity(infoElemsApi + "?tag=tag1", InformationElement[].class);
	assertSuccessful(getInfoElems);

	InformationElement[] infoElemsRes = getInfoElems.getBody();
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

	// Upload to DiMe
	ResponseEntity<SearchEvent[]> uploadRes = 
	    getRest().postForEntity(eventsApi, events, SearchEvent[].class);

	// Check that HTTP was successful
	assertSuccessful(uploadRes);

	// Checks to ensure returned object is the same as uploaded
	SearchEvent[] outEvents = uploadRes.getBody();
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
	
	Message msg = createTestEmail(content1, "");
	MessageEvent event = new MessageEvent();
	event.targettedResource = msg;

	// Upload to DiMe
	ResponseEntity<MessageEvent> uploadRes = 
	    getRest().postForEntity(eventApi, event, MessageEvent.class);

	// Check that HTTP was successful
	assertSuccessful(uploadRes);

	// check that content is still the same
	MessageEvent outEvent = uploadRes.getBody();
	assertEquals(outEvent.targettedResource.plainTextContent, content1);
	Long msgId = outEvent.targettedResource.getId();

	// Change message
	outEvent.targettedResource.plainTextContent = content2;

	dumpData("Changed message", outEvent);
	
	// Upload the changed message
	ResponseEntity<MessageEvent> uploadRes2 = 
	    getRest().postForEntity(eventApi, outEvent, MessageEvent.class);
	
	// Check that HTTP was successful
	assertSuccessful(uploadRes2);

	// check that content is the changed one
	MessageEvent outEvent2 = uploadRes2.getBody();
	assertEquals(outEvent2.targettedResource.plainTextContent, content2);
	assertEquals(msgId, outEvent2.targettedResource.getId());

	// Read back infoelement over REST API and check
	ResponseEntity<Message> getElem = 
	    getRest().getForEntity(infoElemApi + "/" + msgId, Message.class);
	assertSuccessful(getElem);

	Message msg2 = getElem.getBody();
	assertEquals(msg2.plainTextContent, content2);
    }

    @Test
    public void testElemUpload() throws Exception {
	String content1 = "foobar";
	Message msg = createTestEmail(content1, "");

	// Upload to DiMe
	ResponseEntity<Message> uploadRes =
	    getRest().postForEntity(infoElemApi, msg, Message.class);

	// Check that HTTP was successful
	assertSuccessful(uploadRes);

	// check that content is still the same
	Message outMsg = uploadRes.getBody();
	assertEquals(outMsg.plainTextContent, content1);
	Long msgId = outMsg.getId();

	// Read back infoelement over REST API and check
	ResponseEntity<Message> getElem = 
	    getRest().getForEntity(infoElemApi + "/" + msgId, Message.class);
	assertSuccessful(getElem);

	Message msg2 = getElem.getBody();
	assertEquals(msg2.plainTextContent, content1);
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
    	ResponseEntity<String> res = 
    	    getRest().postForEntity(eventApi, event, String.class);
	
	System.out.println("RES=" + res);

    	// Check that HTTP was successful
	assertClientError(res);
    }

}
