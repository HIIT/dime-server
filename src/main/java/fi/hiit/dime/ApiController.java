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

//------------------------------------------------------------------------------

import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.data.*;
import fi.hiit.dime.database.*;
import java.util.List;
import javax.servlet.ServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

//------------------------------------------------------------------------------

@RestController
@RequestMapping("/api")
public class ApiController {
    private static final Logger LOG = 
	LoggerFactory.getLogger(ApiController.class);

    // Mongodb repositories
    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;

    @Autowired
    ApiController(EventDAO eventDAO,
		  InformationElementDAO infoElemDAO) {
	this.eventDAO = eventDAO;
	this.infoElemDAO = infoElemDAO;
    }

    //--------------------------------------------------------------------------

    /** 
	Class for "dummy" API responses which just return a simple message string.
    */
    public class ApiMessage {
	public String message;

	public ApiMessage(String message) {
	    this.message = message;
	}
    }

    //--------------------------------------------------------------------------

    protected User getUser(Authentication auth) {
	CurrentUser currentUser = (CurrentUser)auth.getPrincipal();
	return currentUser.getUser();
    }

    //--------------------------------------------------------------------------

    /**
     * @api {get} /ping Ping server to check availability
     * @apiName GetPing
     * @apiGroup General
     * 
     * @apiSuccess {String} message Dummy message
     * 
     * @apiSuccessExample Success-Response:
     *     HTTP/1.1 200 OK
     *     {
     *       "message": "pong"
     *     }
     */
    @RequestMapping("/ping")
    public ResponseEntity<ApiMessage> ping(ServletRequest req) {
	LOG.info("Received ping from " + req.getRemoteHost());

	HttpHeaders headers = new HttpHeaders();
	headers.setContentType(MediaType.APPLICATION_JSON);
	return new ResponseEntity<ApiMessage>(new ApiMessage("pong"),
					      headers, HttpStatus.OK);
    }

    //--------------------------------------------------------------------------

    /**
     * @api {get} /search Text search
     * @apiName GetSearch
     * @apiGroup Read
     * 
     * @apiParam {String} query Query text to search for
     * @apiParam {Number} limit Maximum number of results returned
     *
     * @apiSuccess {Object[]} - Array of InformationElement objects
     * @apiSuccessExample Success-Response:
     *     HTTP/1.1 200 OK
     *     [
     *       {
     *         "plainTextContent": "Some text content\n",
     *         "user": {
     *           "id": "5524d8ede4b06e42cc0e0aca",
     *           "role": "USER",
     *           "username": "testuser"
     *         },
     *         "stub": false,
     *         "uri": "file:///home/testuser/some_file.txt",
     *         "type": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#TextDocument",
     *         "mimeType": "text/plain",
     *         "timeCreated": 1430142736819,
     *         "id": "d8b5b874e4bae5a6f6260e1042281e91c69d305e",
     *         "timeModified": 1430142736819,
     *         "score": 0.75627613,
     *         "isStoredAs": "http://www.semanticdesktop.org/ontologies/nfo#FileDataObject"
     *       },
     *       {
     *         "plainTextContent": "Some other text content",
     *         "user": {
     *           "id": "5524d8ede4b06e42cc0e0aca",
     *           "role": "USER",
     *           "username": "testuser"
     *         },
     *         "stub": false,
     *         "uri": "file:///home/testuser/another_file.txt",
     *         "type": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#TextDocument",
     *         "mimeType": "text/plain",
     *         "timeCreated": 1430142737246,
     *         "id": "99db4832be27cff6b08a1f91afbf0401cad49d15",
     *         "timeModified": 1430142737246,
     *         "score": 0.75342464,
     *         "isStoredAs": "http://www.semanticdesktop.org/ontologies/nfo#FileDataObject"
     *       }
     *     ]
     *     
     */
    @RequestMapping(value="/search", method = RequestMethod.GET)
    public ResponseEntity<List<InformationElement>>
	search(Authentication auth, 
	       @RequestParam String query,
	       @RequestParam(defaultValue="-1") int limit) {

	User user = getUser(auth);

	List<InformationElement> results = infoElemDAO.textSearch(query, limit, user.id);
	LOG.info(String.format("Search query \"%s\" (limit=%d) returned %d results.",
			       query, limit, results.size()));

	return new ResponseEntity<List<InformationElement>>(results, HttpStatus.OK);
    }

}
