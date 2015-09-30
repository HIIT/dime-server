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
import fi.hiit.dime.data.*;
import fi.hiit.dime.database.*;
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
	ResponseEntity<InformationElement[]> res = 
	    getRest().getForEntity(apiUrl("/search?query=" + query),
				   InformationElement[].class);

	assertSuccessful(res);

	return res.getBody();
    }

    @Test
    public void testSearch() throws Exception {
	final String magicWord = "foobar";

	// Search without events should return zero
	InformationElement[] searchResEmpty = doSearch(magicWord);
    	assertEquals(0, searchResEmpty.length);

	// Create some events with messages
	int numEvents = 10;
	Event[] events = new Event[numEvents];

	Set<Integer> idxToFind = new HashSet<Integer>();
	idxToFind.add(2);
	idxToFind.add(5);
	idxToFind.add(6);
	idxToFind.add(9);

	RandomPassword rand = new RandomPassword();

	for (int i=0; i<numEvents; i++) {
	    String content = rand.getPassword(10, false, false);
	    if (idxToFind.contains(i)) 
		content += " " + magicWord;
	    content += " " + rand.getPassword(10, false, false);
	    Message msg = createTestEmail(content);
	    MessageEvent event = new MessageEvent();
	    event.targettedResource = msg;

	    events[i] = event;
	}

	// Upload them to DiMe
	ResponseEntity<Event[]> res = 
	    getRest().postForEntity(eventsApi, events, Event[].class);

	// Check that HTTP was successful
	assertSuccessful(res);

	// Refresh Lucene index
	if (searchIndex != null)
	    searchIndex.updateIndex(false);

	// Now try searching for the ones in idxToFind
	InformationElement[] searchRes = doSearch(magicWord);

	dumpData("searchRes", searchRes);

    	assertEquals(idxToFind.size(), searchRes.length);
	
    	for (InformationElement elem : searchRes) {
    	    assertTrue(elem.plainTextContent.contains(magicWord));
    	}

	//FIXME: also compare to idxToFind
    }
}
