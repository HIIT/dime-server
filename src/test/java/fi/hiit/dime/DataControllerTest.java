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

    @Autowired 
    private ObjectMapper objectMapper;

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

	String apiEndpoint = apiUrl("/data/event");
	dumpData("Event to be uploaded to " + apiEndpoint, event1);

	// Upload to DiMe
	ResponseEntity<FeedbackEvent> res1 = 
	    getRest().postForEntity(apiEndpoint, event1,
				    FeedbackEvent.class);

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
	Document stubDoc = new Document();
	stubDoc.id = outDoc1.id;

	// Create feedback with the stub document
	FeedbackEvent event2 = new FeedbackEvent();
	event2.value = 0.89;
	event2.targettedResource = stubDoc;

	dumpData("Event with stub to be uploaded to " + apiEndpoint, event2);
	
	ResponseEntity<FeedbackEvent> res2 = 
	    getRest().postForEntity(apiEndpoint, event2,
				    FeedbackEvent.class);

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

    /**
       Test uploading MessageEvent
     */
    @Test
    public void testMessageEvent() throws Exception {
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

	// Create a message event
	MessageEvent event1 = new MessageEvent();
	event1.targettedResource = msg;

	String apiEndpoint = apiUrl("/data/event");
	dumpData("Event to be uploaded to " + apiEndpoint, event1);

	// Upload to DiMe
	ResponseEntity<MessageEvent> res1 = 
	    getRest().postForEntity(apiEndpoint, event1,
				    MessageEvent.class);
	
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

}
