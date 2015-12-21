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

import fi.hiit.dime.ApiController.ApiMessage;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.Message;
import fi.hiit.dime.data.MessageEvent;
import fi.hiit.dime.data.ReadingEvent;
import fi.hiit.dime.data.ResourcedEvent;
import fi.hiit.dime.data.ScientificDocument;
import fi.hiit.dime.data.SearchEvent;
import fi.hiit.dime.search.KeywordSearchQuery;
import fi.hiit.dime.search.SearchIndex;
import fi.hiit.dime.util.RandomPassword;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import static org.junit.Assert.*;

import java.util.HashSet;
import java.util.Set;

/**
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@RunWith(SpringJUnit4ClassRunner.class)
public class ApiControllerTest extends RestTest {
    @Autowired
    SearchIndex searchIndex;

    @Test
    public void testPing() throws Exception {
        ResponseEntity<ApiMessage> res = 
            getRest().getForEntity(apiUrl("/ping"), ApiMessage.class);

        assertSuccessful(res);
        assertEquals(res.getBody().message, "pong");
    }

    @Test
    public void testEmptySearch() throws Exception {
        ResponseEntity<InformationElement[]> res = 
            getRest().getForEntity(apiUrl("/search?query="),
                                   InformationElement[].class);

        assertSuccessful(res);

        InformationElement[] elems = res.getBody();
        assertEquals(0, elems.length);
    }

    private InformationElement[] doSearch(String query) {
        return getData(apiUrl("/search?query=" + query), InformationElement[].class);
    }

    private Event[] doEventSearch(String query) {
        return getData(apiUrl("/eventsearch?query=" + query), Event[].class);
    }

    @Test
    public void testSearch() throws Exception {
        final String magicWord = "foobar";

        // Search without events should return zero
        InformationElement[] searchResEmpty = doSearch(magicWord);
        assertEquals(0, searchResEmpty.length);

        // Create some events with messages
        int numEvents = 12;
        Event[] events = new Event[numEvents];

        Set<Integer> idxToFind = new HashSet<Integer>();
        idxToFind.add(2);
        idxToFind.add(5);
        idxToFind.add(6);
        idxToFind.add(9);

        RandomPassword rand = new RandomPassword();

        for (int i=0; i<numEvents-2; i++) {
            String content = rand.getPassword(10, false, false);
            if (idxToFind.contains(i)) 
                content += " " + magicWord;
            content += " " + rand.getPassword(10, false, false);
            Message msg = createTestEmail(content, "Hello");
            msg.appId = "fgieruhgieruhg_msg_" + i;
            MessageEvent event = new MessageEvent();
            event.targettedResource = msg;

            events[i] = event;
        }
        
        // Make a last event which contains a duplicate message
        MessageEvent extraEvent = new MessageEvent();
        extraEvent.targettedResource = ((MessageEvent)events[5]).targettedResource;

        events[numEvents-2] = extraEvent;

        SearchEvent searchEvent = new SearchEvent();
        searchEvent.query = "foobar";
        searchEvent.appId = "i43ruhutfiu5rhuhuhg";
        
        events[numEvents-1] = searchEvent;

        dumpData("TESTSEARCH", events);

        // Upload them to DiMe
        Event[] uploadedEvents = uploadEvents(events, Event[].class);

        assertEquals(numEvents, uploadedEvents.length);

        // Record ids of messages to be found by search
        Set<Long> idToFind = new HashSet<Long>();
        for (int i=0; i<numEvents-1; i++) {
            if (idxToFind.contains(i))
                idToFind.add(((MessageEvent)uploadedEvents[i]).targettedResource.getId());
        }

        // Now try searching for the ones in idxToFind
        InformationElement[] searchRes = doSearch(magicWord+"&@type=Message");

        dumpData("searchRes", searchRes);

        // Check that we have the expected number of results
        assertEquals(idxToFind.size(), searchRes.length);
        
        Set<Long> idFound = new HashSet<Long>();
        for (InformationElement elem : searchRes) {
            // Check that each returned document contains the expected word
            assertTrue(elem.plainTextContent.contains(magicWord));
            idFound.add(elem.getId());
        }

        // Check that the ids are exactly those expected
        assertEquals(idToFind, idFound);

        // Try searching as events
        Event[] searchEventsRes = doEventSearch(magicWord+"&@type=Message");
        
        dumpData("searchEventsRes", searchEventsRes);

        // Check that we have the expected number of results
        // +1 because we added an extra event with duplicate msg
        assertEquals(idxToFind.size()+1, searchEventsRes.length);
        
        Set<Long> idFound2 = new HashSet<Long>();
        for (Event event : searchEventsRes) {
            assertTrue(event instanceof ResourcedEvent);

            ResourcedEvent revent = (ResourcedEvent)event;
            //assertTrue(revent.targettedResource.plainTextContent.contains(magicWord));

            idFound2.add(revent.targettedResource.getId());
        }

        // Check that the ids are exactly those expected
        assertEquals(idToFind, idFound2);

        // Search for SearchEvents only
        Event[] searchByTypeRes = doEventSearch("foobar&@type=SearchEvent");

        assertEquals(1, searchByTypeRes.length);
        assertEquals(searchEvent.appId, searchByTypeRes[0].appId);
        assertTrue(searchByTypeRes[0] instanceof SearchEvent);
        assertEquals(searchEvent.query, ((SearchEvent)searchByTypeRes[0]).query);
    }

    @Test
    public void testReadingEventSearch() throws Exception {
        String magicText = "foobarbaz";
        ScientificDocument doc = createScientificDocument(randomText);
        ReadingEvent re = createReadingEvent(doc, magicText);
        re.appId = "hgfewiuhoi543rughierh";

        uploadEvent(re, ReadingEvent.class);

        Event[] searchEventsRes = doEventSearch(magicText);
        
        dumpData("searchEventsRes", searchEventsRes);

        assertEquals(1, searchEventsRes.length);

        assertTrue(searchEventsRes[0] instanceof ReadingEvent);

        ReadingEvent res = (ReadingEvent)searchEventsRes[0];

        assertEquals(re.appId, res.appId);
        assertEquals(re.plainTextContent, res.plainTextContent);

        // Because we are nulling the document content
        assertEquals(null, res.targettedResource.plainTextContent);     
    }

    @Test
    public void testKeywordSearch() throws Exception {
        String magicText = "foobarbaz";
        ScientificDocument doc = createScientificDocument(randomText);
        ReadingEvent re = createReadingEvent(doc, magicText);
        re.appId = "hgfewiuhoi543rughierh";

        uploadEvent(re, ReadingEvent.class);

        KeywordSearchQuery query = new KeywordSearchQuery();
        query.add("foobarbaz", 0.4);
        query.add("tellus", 0.1);

        dumpData("query", query);
        Event[] res = uploadData(apiUrl("/eventkeywordsearch"), query.weightedKeywords,
                                 Event[].class);

        dumpData("keyword search results", res);
        assertEquals(1, res.length);
    }
}
