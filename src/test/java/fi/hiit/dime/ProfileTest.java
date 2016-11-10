/*
  Copyright (c) 2016 University of Helsinki

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

import fi.hiit.dime.data.DesktopEvent;
import fi.hiit.dime.data.Document;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.data.Tag;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.SpringApplicationConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.Date;

/**
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@SpringApplicationConfiguration(classes = Application.class)
@RunWith(SpringJUnit4ClassRunner.class)
public class ProfileTest {
    @Test
    public void testEvents() throws Exception {
        Profile p = new Profile("My Re:Know profile");
        p.tags.add(new Tag("reknow"));
        p.tags.add(new Tag("dime"));
        p.tags.add(new Tag("knowledge work"));

        assertEquals(3, p.tags.size());

        // Create some documents
        Document doc1 = new Document();
        doc1.uri = "http://www.example.com/dime.txt";
        doc1.plainTextContent = "DiMe is awesome!!!";
        doc1.mimeType = "text/plain";

        Document doc2 = new Document();
        doc2.uri = "http://www.example.com/reknow.txt";
        doc2.plainTextContent = "Revolution of Knowledge Work is funded by Tekes, as a large strategic opening.";
        doc2.mimeType = "text/plain";

        // Create feedback, with document embedded
        DesktopEvent event1 = new DesktopEvent();
        event1.targettedResource = doc1;
        event1.actor = "MyPdfReader";
        event1.start = new Date();

        p.addEvent(event1, 0.5, "FooAlgorithm");
        p.addEvent(event1, 0.6, "FooAlgorithm");
        p.addInformationElement(doc2, 0.9, "BarAlgorithm");

        assertEquals(0, p.validatedEvents.size());
        assertEquals(0, p.validatedInformationElements.size());
        assertEquals(1, p.suggestedEvents.size());
        assertEquals(0.6, p.suggestedEvents.get(0).weight, 0.0001);
        assertEquals(1, p.suggestedInformationElements.size());
        
        p.validateEvent(event1, 0.9, "FooInterface");
        assertEquals(1, p.validatedEvents.size());
        assertEquals(0, p.validatedInformationElements.size());
        assertEquals(1, p.suggestedEvents.size());
        assertEquals(1, p.suggestedInformationElements.size());

        p.validateInformationElement(doc2, 0.9, "BarInterface");
        assertEquals(1, p.validatedEvents.size());
        assertEquals(1, p.validatedInformationElements.size());
        assertEquals(1, p.suggestedEvents.size());
        assertEquals(1, p.suggestedInformationElements.size());
    }
}
