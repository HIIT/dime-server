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

import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.ResourcedEvent;
import fi.hiit.dime.database.EventDAO;
import fi.hiit.dime.database.InformationElementDAO;
import fi.hiit.dime.search.KeywordSearchQuery;
import fi.hiit.dime.search.SearchIndex;
import fi.hiit.dime.search.SearchQuery;
import fi.hiit.dime.search.TextSearchQuery;
import fi.hiit.dime.search.WeightedKeyword;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import javax.servlet.ServletRequest;

/**
 * General API controller, for things that go directly under the /api
 * REST endpoint.
 *
 * @author Mats Sjöberg, mats.sjoberg@helsinki.fi
 */
@RestController
@RequestMapping("/api")
public class ApiController extends AuthorizedController {
    private static final Logger LOG = LoggerFactory.getLogger(ApiController.class);

    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;

    @Autowired
    private DiMeProperties dimeConfig;

    @Autowired
    SearchIndex searchIndex;

    @Autowired
    ApiController(EventDAO eventDAO,
		  InformationElementDAO infoElemDAO) {
	this.eventDAO = eventDAO;
	this.infoElemDAO = infoElemDAO;
    }

    /** 
	Class for "dummy" API responses which just return a simple
	message string.
    */
    public static class ApiMessage {
	public String message;

	public ApiMessage() {}

	public ApiMessage(String message) {
	    this.message = message;
	}
    }

    @RequestMapping("/ping")
    public ResponseEntity<ApiMessage> ping(ServletRequest req) {
	LOG.info("Received ping from " + req.getRemoteHost());

	HttpHeaders headers = new HttpHeaders();
	headers.setContentType(MediaType.APPLICATION_JSON);
	return new ResponseEntity<ApiMessage>(new ApiMessage("pong"),
					      headers, HttpStatus.OK);
    }

    /**
       Helper method to transform the search results into an
       appropriate format for returning from the API.
    */
    protected InformationElement[] doSearch(SearchQuery query, int limit, User user)
	throws IOException 
    {
	if (query.isEmpty()) {
	    LOG.debug("query empty");
	    return new InformationElement[0];
	}

	searchIndex.updateIndex(true);
	
	List<InformationElement> resList = searchIndex.search(query, limit, user.getId());

	InformationElement[] results = new InformationElement[resList.size()];
	resList.toArray(results);	

	LOG.info(String.format("Search query \"%s\" (limit=%d) returned %d results.",
			       query, limit, results.length));
	return results;
    }

    /**
       Helper method to transform the information element search
       results into their corresponding events for returning from the
       API.
    */
    protected Event[] doEventSearch(SearchQuery query, int limit, User user) 
	throws IOException 
    {
	if (query.isEmpty())
	    return new Event[0];

	searchIndex.updateIndex(true);
	List<InformationElement> resList = searchIndex.search(query, limit, user.getId());

	List<Event> events = new ArrayList<Event>();
	for (InformationElement elem : resList) {
	    List<ResourcedEvent> expandedEvents = eventDAO.findByElement(elem, user);
	    for (ResourcedEvent event : expandedEvents) {
		event.targettedResource.plainTextContent = null;
		event.score = event.targettedResource.score;
	    }
	    events.addAll(expandedEvents);
	}
	    
	Event[] results = new Event[events.size()];
	events.toArray(results);

	LOG.info(String.format("Search query \"%s\" (limit=%d) returned %d results.",
			       query, limit, results.length));
		
	return results;
    }

    @RequestMapping(value="/search", method = RequestMethod.GET)
    public ResponseEntity<InformationElement[]> 
	search(Authentication auth, 
	       @RequestParam String query,
	       @RequestParam(defaultValue="-1") int limit) 
    {
	User user = getUser(auth);
	LOG.debug("foo1 = " + query);

	try {
	    TextSearchQuery textQuery = new TextSearchQuery(query);
	    InformationElement[] results = doSearch(textQuery, limit, user);

	    return new ResponseEntity<InformationElement[]>(results, HttpStatus.OK);
	} catch (IOException e) {
	    return new ResponseEntity<InformationElement[]>
		(HttpStatus.INTERNAL_SERVER_ERROR);
	}
    }

    @RequestMapping(value="/eventsearch", method = RequestMethod.GET)
    public ResponseEntity<Event[]>
	eventSearch(Authentication auth, 
		    @RequestParam String query,
		    @RequestParam(defaultValue="-1") int limit) {
	User user = getUser(auth);

	try {
	    TextSearchQuery textQuery = new TextSearchQuery(query);
	    Event[] results = doEventSearch(textQuery, limit, user);

	    return new ResponseEntity<Event[]>(results, HttpStatus.OK);
	} catch (IOException e) {
	    return new ResponseEntity<Event[]> (HttpStatus.INTERNAL_SERVER_ERROR);
	}
    }
	
    @RequestMapping(value="/keywordsearch", method = RequestMethod.POST)
    public ResponseEntity<InformationElement[]>
	search(Authentication auth, @RequestBody WeightedKeyword[] input) 
    {
	User user = getUser(auth);

	try {
	    KeywordSearchQuery query = new KeywordSearchQuery(input);
	    InformationElement[] results = doSearch(query, -1, user);
	    
	    return new ResponseEntity<InformationElement[]>(results, HttpStatus.OK);
	} catch (IOException e) {
	    return new ResponseEntity<InformationElement[]>
		(HttpStatus.INTERNAL_SERVER_ERROR);
	}
    }

    @RequestMapping(value="/eventkeywordsearch", method = RequestMethod.POST)
    public ResponseEntity<Event[]>
	eventSearch(Authentication auth, @RequestBody WeightedKeyword[] input) 
    {
	User user = getUser(auth);

	try {
	    KeywordSearchQuery query = new KeywordSearchQuery(input);
	    Event[] results = doEventSearch(query, -1, user);

	    return new ResponseEntity<Event[]>(results, HttpStatus.OK);
	} catch (IOException e) {
	    return new ResponseEntity<Event[]> (HttpStatus.INTERNAL_SERVER_ERROR);
	}
    }

}
