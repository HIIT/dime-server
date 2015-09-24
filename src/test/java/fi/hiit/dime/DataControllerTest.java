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

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import static org.junit.Assert.*;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@RunWith(SpringJUnit4ClassRunner.class)
public class DataControllerTest extends RestTest {
    private static final double DELTA = 1e-10;

    private String eventApi, eventsApi, infoElemApi, infoElemsApi;

    @Autowired 
    private ObjectMapper objectMapper;

    @Override
    protected void setup() {
	eventApi = apiUrl("/data/event");
	eventsApi = apiUrl("/data/events");
	infoElemApi = apiUrl("/data/informationelement");
	infoElemsApi = apiUrl("/data/informationelements");
    }

    /**
     * Helper method to print out the content of a DiMeData object.
     */
    private void dumpData(String message, DiMeData data) {
	try {
	    System.out.println(message + "\n" +
			       objectMapper.writerWithDefaultPrettyPrinter().
			       writeValueAsString(data));
	} catch (IOException e) {
	}
    }

    /**
     * Helper method to print out the content of an array of DiMeData objects.
     */
    private void dumpData(String message, DiMeData[] data) {
	try {
	    for (int i=0; i<data.length; i++) {
		String dataStr = objectMapper.
		    writerWithDefaultPrettyPrinter().writeValueAsString(data[i]);
		System.out.println(String.format("%s [%d]: %s", message, i, dataStr));
	    }
	} catch (IOException e) {
	}
    }

    /**
       Tests uploading event
       - checks that stubs work (if second upload gets expanded)
       - checks that specifying @type works
    */
    @Test
    public void testEventUpload() throws Exception {
	// Create a document
	Document doc = new Document();
	doc.uri = "http://www.example.com/hello.txt";
	doc.plainTextContent = "Hello, world";
	doc.mimeType = "text/plain";

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

	// InformationElement outDoc1 = outEvent1.targettedResource;
	Document outDoc1 = (Document)outEvent1.targettedResource;
	assertEquals(doc.uri, outDoc1.uri);
	assertEquals(doc.plainTextContent, outDoc1.plainTextContent);
	assertEquals(doc.mimeType, outDoc1.mimeType); 

	// Create a "stub" document, i.e. that refers to the
	// previously uploaded one
	InformationElement stubDoc = new InformationElement();
	stubDoc.id = outDoc1.id;

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
	assertEquals(outDoc1.id, outDoc2.id);
	assertEquals(doc.uri, outDoc2.uri);
	assertEquals(doc.mimeType, outDoc2.mimeType);

	/* This is not returned at the moment, since we don't want to
	   duplicate the huge plainTextContent field... */
	//assertEquals(doc.plainTextContent, outDoc2.plainTextContent);
    }

    protected Message createTestEmail() {
	// Create a message
	Message msg = new Message();
	msg.date = new Date(); // current date
	msg.subject = "Hello DiMe";
	msg.fromString = "Mats Sjöberg <mats.sjoberg@helsinki.fi>";
	msg.toString = "Mats Sjöberg <mats.sjoberg@hiit.fi>";
	msg.ccString = "Mats Sjöberg <mats.sjoberg@cs.helsinki.fi>";
	msg.plainTextContent = "Hello, world";
	
	SimpleDateFormat format =
	    new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss Z");
	
	msg.rawMessage = 
	    "From: " + msg.fromString + "\n" +
	    "To: " + msg.toString + "\n" +
	    "Cc: " + msg.ccString + "\n" + 
	    "Subject: " + msg.subject + "\n" +
	    "Date: " + format.format(msg.date) +
	    "Message-ID: <43254843985749@helsinki.fi>\n" + 
	    "\n\n" + msg.plainTextContent;

	return msg;
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
	event1.addTag("eventTag1");
	event1.addTag("foo");
	events[0] = event1;

	SearchEvent event2 = new SearchEvent();
	event2.query = "some search query";
	event2.actor = "TestActor1";
	events[1] = event2;

	SearchEvent event3 = new SearchEvent();
	event3.query = "some other search query";
	event3.actor = "TestActor2";
	event3.addTag("foo");
	event3.addTag("bar");
	events[2] = event3;

	// Create a message event
	Message emailMsg = createTestEmail();
	emailMsg.addTag("tag2");
	
	MessageEvent event4 = new MessageEvent();
	event4.targettedResource = emailMsg;
	events[3] = event4;
    
	dumpData("List of events to be uploaded to " + eventsApi, events);

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

	dumpData("Events received back from server:", outEvents);

	// Read back events over REST API and check
	ResponseEntity<FeedbackEvent> getRes1 = 
	    getRest().getForEntity(eventApi + "/" + outEvent1.id,
				   FeedbackEvent.class);
	assertSuccessful(getRes1);

	FeedbackEvent getEvent1 = getRes1.getBody();
	assertEquals(event1.value, getEvent1.value, DELTA);
	assertEquals(getEvent1.tags.size(), 2);
	assertTrue(getEvent1.hasTag("eventTag1"));

	Document getDoc = (Document)getEvent1.targettedResource;
	assertEquals(origDoc.uri, getDoc.uri);
	assertEquals(getDoc.tags.size(), 2);
	assertTrue(getDoc.hasTag("tag1"));
	assertTrue(getDoc.hasTag("tag2"));

	ResponseEntity<SearchEvent> getRes2 = 
	    getRest().getForEntity(eventApi + "/" + outEvent2.id,
				   SearchEvent.class);

	SearchEvent getEvent2 = getRes2.getBody();
	assertEquals(event2.query, getEvent2.query);

	ResponseEntity<SearchEvent> getRes3 = 
	    getRest().getForEntity(eventApi + "/" + outEvent3.id,
				   SearchEvent.class);

	SearchEvent getEvent3 = getRes3.getBody();
	assertEquals(event3.query, getEvent3.query);

	// Read back uploaded document
	ResponseEntity<Document> getDocRes = 
	    getRest().getForEntity(infoElemApi + "/" + uploadDoc.id,
				   Document.class);
	assertSuccessful(getDocRes);

	Document getDirectDoc = getDocRes.getBody();
	assertEquals(getDirectDoc.uri, origDoc.uri);

	// Also test accessing an object that doesn't exist
	ResponseEntity<Document> getBadRes1 = 
	    getRest().getForEntity(infoElemApi + "/foobar42",
				   Document.class);
	assertClientError(getBadRes1);

	// Also test accessing an object that doesn't exist
	ResponseEntity<SearchEvent> getBadRes2 = 
	    getRest().getForEntity(eventApi + "/foobar42",
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

	// Test filtering on tag
	ResponseEntity<Event[]> getEventsRes2 = 
	    getRest().getForEntity(eventsApi + "?tag=foo",
				   Event[].class);
	assertSuccessful(getEventsRes2);

	Event[] eventsRes2 = getEventsRes2.getBody();
	assertEquals(2, eventsRes2.length);

	for (Event ev : eventsRes2) {
	    assertTrue(ev.hasTag("foo"));
	}

	dumpData("events filtered by tag", eventsRes2);

	// Test filtering by bad parameters
	ResponseEntity<Event[]> getEventsRes3 = 
	    getRest().getForEntity(eventsApi + "?foo=bar",
				   Event[].class);
	assertClientError(getEventsRes3);

	// Test filtering on multiple parameters
	ResponseEntity<SearchEvent[]> getEventsRes4 = 
	    getRest().getForEntity(eventsApi + "?query=" + event3.query
				   + "&tag=foo",
				   SearchEvent[].class);
	assertSuccessful(getEventsRes4);

	SearchEvent[] eventsRes4 = getEventsRes4.getBody();
	assertEquals(1, eventsRes4.length);

	assertEquals(eventsRes4[0].query, event3.query);
	assertTrue(eventsRes4[0].hasTag("foo"));

	// Test filtering for information elements
	ResponseEntity<InformationElement[]> getInfoElems = 
	    getRest().getForEntity(infoElemsApi + "?tag=tag2", InformationElement[].class);
	assertSuccessful(getInfoElems);

	InformationElement[] infoElemsRes = getInfoElems.getBody();
	assertEquals(2, infoElemsRes.length);

	for (InformationElement elem : infoElemsRes) {
	    assertTrue(elem.hasTag("tag2"));
	}

	dumpData("info elems filtered by tag", infoElemsRes);
    }
}
