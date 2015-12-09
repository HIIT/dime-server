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
import fi.hiit.dime.data.DiMeData;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.ResourcedEvent;
import fi.hiit.dime.database.EventDAO;
import fi.hiit.dime.database.InformationElementDAO;
import fi.hiit.dime.search.KeywordSearchQuery;
import fi.hiit.dime.search.SearchIndex;
import fi.hiit.dime.search.SearchQuery;
import fi.hiit.dime.search.SearchResults;
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
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
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
    protected SearchResults doSearch(SearchQuery query, int limit, User user)
        throws IOException
    {
        if (query.isEmpty())
            return new SearchResults();

        searchIndex.updateIndex(true);

        SearchResults res = searchIndex.search(query, limit, user.getId());

        List<DiMeData> elemList = new ArrayList<DiMeData>();
        Set<Long> seen = new HashSet<Long>();

        for (DiMeData data : res.getDocs()) {
            InformationElement elem = null;
            if (data instanceof InformationElement)
                elem = (InformationElement)data;
            else if (data instanceof ResourcedEvent)
                elem = ((ResourcedEvent)data).targettedResource;

            if (elem != null && !seen.contains(elem.getId())) {
                elemList.add(elem);
                seen.add(elem.getId());
            }
        }

        res.setDocs(elemList);

        LOG.info("Search query \"{}\" (limit={}) returned {} results.",
                 query, limit, res.getNumFound());
        return res;
    }

    /**
       Helper method to transform the information element search
       results into their corresponding events for returning from the
       API.
    */
    protected SearchResults doEventSearch(SearchQuery query, int limit,
                                          User user)
        throws IOException
    {
        if (query.isEmpty())
            return new SearchResults();

        searchIndex.updateIndex(true);
        SearchResults res = searchIndex.search(query, limit, user.getId());

        List<DiMeData> events = new ArrayList<DiMeData>();
        Set<Long> seen = new HashSet<Long>();

        for (DiMeData data : res.getDocs()) {
            if (data instanceof InformationElement) {
                List<ResourcedEvent> expandedEvents =
                    eventDAO.findByElement((InformationElement)data, user);
                for (ResourcedEvent event : expandedEvents) {
                    event.targettedResource.plainTextContent = null;
                    event.score = event.targettedResource.score;
                    if (!seen.contains(event.getId())) {
                        events.add(event);
                        seen.add(event.getId());
                    }
                }
            } else if (data instanceof Event) {
                Event event = (Event)data;
                if (!seen.contains(event.getId())) {
                    if (event instanceof ResourcedEvent) {
                        ResourcedEvent re = (ResourcedEvent)event;
                        re.targettedResource.plainTextContent = null;
                    }
                    events.add(event);
                    seen.add(event.getId());
                }
            }
        }

        res.setDocs(events);

        LOG.info("Search query \"{}\" (limit={}) returned {} results.",
                 query, limit, res.getNumFound());

        return res;
    }

    @RequestMapping(value="/search", method = RequestMethod.GET)
    public ResponseEntity<SearchResults>
        search(Authentication auth,
               @RequestParam String query,
               @RequestParam(defaultValue="-1") int limit)
    {
        User user = getUser(auth);

        try {
            TextSearchQuery textQuery = new TextSearchQuery(query);
            SearchResults results = doSearch(textQuery, limit, user);

            return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
        } catch (IOException e) {
            return new ResponseEntity<SearchResults>
                (HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @RequestMapping(value="/eventsearch", method = RequestMethod.GET)
    public ResponseEntity<SearchResults>
        eventSearch(Authentication auth,
                    @RequestParam String query,
                    @RequestParam(defaultValue="-1") int limit) {
        User user = getUser(auth);

        try {
            TextSearchQuery textQuery = new TextSearchQuery(query);
            SearchResults results = doEventSearch(textQuery, limit, user);

            return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
        } catch (IOException e) {
            return new ResponseEntity<SearchResults>
                (HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @RequestMapping(value="/keywordsearch", method = RequestMethod.POST)
    public ResponseEntity<SearchResults>
        search(Authentication auth, @RequestBody WeightedKeyword[] input) 
    {
        User user = getUser(auth);

        try {
            KeywordSearchQuery query = new KeywordSearchQuery(input);
            SearchResults results = doSearch(query, -1, user);
            return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
        } catch (IOException e) {
            return new ResponseEntity<SearchResults>
                (HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @RequestMapping(value="/eventkeywordsearch", method = RequestMethod.POST)
    public ResponseEntity<SearchResults>
        eventSearch(Authentication auth, @RequestBody WeightedKeyword[] input) 
    {
        User user = getUser(auth);

        try {
            KeywordSearchQuery query = new KeywordSearchQuery(input);
            SearchResults results = doEventSearch(query, -1, user);

            return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
        } catch (IOException e) {
            return new ResponseEntity<SearchResults>
                (HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

}
