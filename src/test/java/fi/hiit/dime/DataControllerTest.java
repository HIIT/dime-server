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

    @Test
    public void testFeedbackEvent() throws Exception {
	// Create a document
	Document doc = new Document();
	doc.uri = "http://www.example.com/hello.txt";
	doc.plainTextContent = "Hello, world";
	doc.mimeType = "text/plain";

	// Create feedback, with document embedded
	FeedbackEvent event1 = new FeedbackEvent();
	event1.value = 0.42;
	event1.targettedResource = doc;

	String api1 = apiUrl("/data/event");
	dumpData("Event to be uploaded to " + api1, event1);

	// Upload to DiMe
	ResponseEntity<FeedbackEvent> res1 = getRest().postForEntity(api1, event1,
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

	String api2 = apiUrl("/data/event");
	dumpData("Event with stub to be uploaded to " + api2, event2);
	
	ResponseEntity<FeedbackEvent> res2 = getRest().postForEntity(api2, event2,
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

}
