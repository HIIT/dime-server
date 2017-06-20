/*
  Copyright (c) 2015-2016 University of Helsinki

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

import static fi.hiit.dime.search.SearchIndex.weightType;

import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import javax.servlet.ServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.danubetech.libsovrin.SovrinConstants;
import com.danubetech.libsovrin.ledger.Ledger;
import com.danubetech.libsovrin.ledger.LedgerResults.BuildAttribRequestResult;
import com.danubetech.libsovrin.ledger.LedgerResults.BuildNymRequestResult;
import com.danubetech.libsovrin.ledger.LedgerResults.SignAndSubmitRequestResult;
import com.danubetech.libsovrin.signus.Signus;
import com.danubetech.libsovrin.signus.SignusJSONParameters.CreateAndStoreMyDidJSONParameter;
import com.danubetech.libsovrin.signus.SignusResults.CreateAndStoreMyDidResult;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.database.EventDAO;
import fi.hiit.dime.database.InformationElementDAO;
import fi.hiit.dime.database.ProfileDAO;
import fi.hiit.dime.search.KeywordSearchQuery;
import fi.hiit.dime.search.SearchIndex;
import fi.hiit.dime.search.SearchIndex.SearchQueryException;
import fi.hiit.dime.search.SearchIndex.WeightType;
import fi.hiit.dime.search.SearchQuery;
import fi.hiit.dime.search.SearchResults;
import fi.hiit.dime.search.TextSearchQuery;
import fi.hiit.dime.search.WeightedKeyword;
import fi.hiit.dime.sovrin.SovrinService;
import fi.hiit.dime.xdi.XdiService;
import xdi2.client.exceptions.Xdi2ClientException;
import xdi2.client.impl.http.XDIHttpClient;
import xdi2.client.impl.local.XDILocalClient;
import xdi2.core.Graph;
import xdi2.core.syntax.XDIAddress;
import xdi2.core.util.XDIAddressUtil;
import xdi2.messaging.Message;
import xdi2.messaging.MessageEnvelope;
import xdi2.messaging.container.MessagingContainer;

/**
 * General API controller, for things that go directly under the /api
 * REST endpoint.
 *
 * @author Mats Sjöberg, mats.sjoberg@helsinki.fi
 */
@RestController
@RequestMapping("/api")
public class ApiController extends AuthorizedController {
	private static final Logger LOG =
			LoggerFactory.getLogger(ApiController.class);

	public static final int RETRIES = 3;

	private final EventDAO eventDAO;
	private final InformationElementDAO infoElemDAO;
	private final ProfileDAO profileDAO;

	@Value("${application.formatted-version}")
	private String dimeVersion;

	@Autowired
	private DiMeProperties dimeConfig;

	@Autowired
	SearchIndex searchIndex;

	@Autowired 
	private ObjectMapper objectMapper;

	@Autowired
	ApiController(EventDAO eventDAO,
			InformationElementDAO infoElemDAO,
			ProfileDAO profileDAO) {
		this.eventDAO = eventDAO;
		this.infoElemDAO = infoElemDAO;
		this.profileDAO = profileDAO;
	}

	/**
        Class for "dummy" API responses which just return a simple
        message string.
	 */
	@JsonInclude(value=JsonInclude.Include.NON_NULL)
	public static class ApiMessage {
		public String message;
		public String version;
		public String userId;
	}

	/**
        @api {get} /ping Ping server
        @apiName Ping
        @apiDescription A way to "ping" the dime-server to see if it's running, and there is network access. Also returns the DiMe server version.  Authentication is optional, but if you're authenticated it also returns the userId of the authenticated user.

        @apiExample {python} Example usage:
            r = requests.post(server_url + '/ping',
                              timeout=10)         # e.g. in case of network problems
            ok = r.status_code == requests.codes.ok

        @apiSuccessExample {json} Example successful response:
            HTTP/1.1 200 OK
            {
                "message": "pong",
                "version": "v0.1.2",
                "userId": "15524094-5a7c-4b22-8bcd-ddb987a0dd85"
            }
        @apiGroup Status
        @apiVersion 0.1.2
	 */
	@RequestMapping("/ping")
	public ResponseEntity<ApiMessage> ping(Authentication auth, ServletRequest req) {
		LOG.info("Received ping from " + req.getRemoteHost());

		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);

		ApiMessage msg = new ApiMessage();
		msg.message = "pong";
		msg.version = dimeVersion;
		msg.userId = null;
		if (auth != null)
			msg.userId = getUser(auth).userId;

		return new ResponseEntity<ApiMessage>(msg, headers, HttpStatus.OK);
	}

	@JsonInclude(value=JsonInclude.Include.NON_NULL)
	public static class LeaderboardPayload {
		public String userId;
		public String username;
		public Long eventCount;
		public Double time;
	}

	/** @api {post} /updateleaderboard Update event count to the DiMe leaderboard
        @apiName UpdateLeaderboard
        @apiDescription On success, the response will be the JSON object returned by the leaderboard server.

        @apiSuccessExample {json} Example successful response:
            HTTP/1.1 200 OK
            {
                "username": "testuser",
                "eventCount": 12,
                "time": 1478859922942.0,
                "userId": "15524094-5a7c-4b22-8bcd-ddb987a0dd85"
            }
        @apiPermission user
        @apiGroup Status
        @apiVersion 0.2.0
	 */
	@ResponseStatus(value = HttpStatus.NO_CONTENT)
	@RequestMapping(value="/updateleaderboard", method = RequestMethod.POST)
	public ResponseEntity<LeaderboardPayload> updateLeaderboard(Authentication auth) {
		User user = getUser(auth);

		LeaderboardPayload payload = new LeaderboardPayload();
		payload.userId = user.userId;
		payload.username = user.username;
		payload.eventCount = eventDAO.count(user);

		RestTemplate rest = new RestTemplate();
		String endpoint = dimeConfig.getLeaderboardEndpoint();
		ResponseEntity<LeaderboardPayload> res = 
				rest.postForEntity(endpoint, payload, LeaderboardPayload.class);
		assert(res.getStatusCode().is2xxSuccessful());

		LOG.info("Response from leaderboard ({}):", endpoint);
		try {
			LOG.info(objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(res.getBody()));
		} catch (IOException e) {
		}

		return new ResponseEntity<LeaderboardPayload>(res.getBody(), HttpStatus.OK);
	}

	private Profile getProfile(Long profileId, User user) 
			throws NotFoundException 
	{
		Profile profile = profileDAO.findById(profileId, user);

		if (profile == null || !profile.user.getId().equals(user.getId()))
			throw new NotFoundException("Profile not found");
		return profile;
	}

	/** @api {post} /sendtopeoplefinder Upload profile to People Finder service
        @apiName SendToPeopleFinder
        @apiParam {Number} id The profile id
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Status
        @apiVersion 0.2.1
	 */
	@ResponseStatus(value = HttpStatus.NO_CONTENT)
	@RequestMapping(value="/sendtopeoplefinder/{id}", method = RequestMethod.POST)
	public ResponseEntity sendToPeopleFinder(Authentication auth, @PathVariable Long id)
			throws NotFoundException
	{
		User user = getUser(auth);
		Profile profile = getProfile(id, user);

		LOG.info("Send to people finder, user {}, profile {}", user.username, profile.name);

		// create DID in Sovrin

		XDIAddress didXDIAddress = XdiService.getProfileDidXDIAddress(profile);

		if (didXDIAddress == null) {

			try {

				// create USER DID

				CreateAndStoreMyDidJSONParameter createAndStoreMyDidJSONParameter = new CreateAndStoreMyDidJSONParameter(null, null, null, null);
				CreateAndStoreMyDidResult createAndStoreMyDidResult = Signus.createAndStoreMyDid(SovrinService.get().getWallet(), createAndStoreMyDidJSONParameter).get();
				LOG.info("CreateAndStoreMyDidResult: " + createAndStoreMyDidResult);

				String did = createAndStoreMyDidResult.getDid();
				String verkey = createAndStoreMyDidResult.getVerkey();

				// NYM request

				BuildNymRequestResult buildNymRequestResult = null;
				SignAndSubmitRequestResult signAndSubmitRequestResult = null;

				for (int i=0; i<RETRIES; i++) {

					try {

						buildNymRequestResult = Ledger.buildNymRequest(SovrinService.TRUSTEE_VERKEY, did, verkey, null, SovrinConstants.ROLE_STEWARD).get(2, TimeUnit.SECONDS);
						LOG.info("Retry #" + i + ": Success: " + buildNymRequestResult);
						break;
					} catch (TimeoutException ex) {

						LOG.warn("Retry #" + i + ": " + ex.getMessage());
						if (i+1 < RETRIES) continue; else throw ex;
					}
				}

				for (int i=0; i<RETRIES; i++) {

					try {

						signAndSubmitRequestResult = Ledger.signAndSubmitRequest(SovrinService.get().getPool(), SovrinService.get().getWallet(), SovrinService.TRUSTEE_DID, buildNymRequestResult.getRequestJson()).get(2, TimeUnit.SECONDS);
						LOG.info("Retry #" + i + ": Success: " + signAndSubmitRequestResult);
						break;
					} catch (TimeoutException ex) {

						LOG.warn("Retry #" + i + ": " + ex.getMessage());
						if (i+1 < RETRIES) continue; else throw ex;
					}
				}

				// done

				didXDIAddress = XdiService.XDIAddressFromDidString(did);

				LOG.info("Created DID in Sovrin: " + didXDIAddress + " with verkey " + verkey);
				XdiService.setProfileDidXDIAddress(profile, didXDIAddress);
			} catch (Exception ex) {

				throw new RuntimeException("Cannot create DID in Sovrin: " + ex.getMessage(), ex);
			}
		}

		// set host in Sovrin

		String uri = dimeConfig.getBaseUri();
		if (uri == null) uri = "http://localhost:8080/";
		if (! uri.endsWith("/")) uri += "/";
		uri += "xdi/dime/" + didXDIAddress.toString();

		if (uri != null) {

			try {

				String did = XdiService.didStringFromXDIAddress(didXDIAddress);

				// ATTRIB request

				BuildAttribRequestResult buildAttribRequestResult = null;
				SignAndSubmitRequestResult signAndSubmitRequestResult = null;

				for (int i=0; i<RETRIES; i++) {

					try {

						buildAttribRequestResult = Ledger.buildAttribRequest(did, did, null, "{\"endpoint\":{\"xdi\":\"" + uri.replace("\"", "\\\"") + "\"}}", null).get(1, TimeUnit.SECONDS);
						LOG.info("Retry #" + i + ": Success: " + buildAttribRequestResult);
						break;
					} catch (TimeoutException ex) {

						LOG.warn("Retry #" + i + ": " + ex.getMessage());
						if (i+1 < RETRIES) continue; else throw ex;
					}
				}

				for (int i=0; i<RETRIES; i++) {

					try {

						signAndSubmitRequestResult = Ledger.signAndSubmitRequest(SovrinService.get().getPool(), SovrinService.get().getWallet(), did, buildAttribRequestResult.getRequestJson()).get(1, TimeUnit.SECONDS);
						LOG.info("Retry #" + i + ": Success: " + signAndSubmitRequestResult);
						break;
					} catch (TimeoutException ex) {

						LOG.warn("Retry #" + i + ": " + ex.getMessage());
						if (i+1 < RETRIES) continue; else throw ex;
					}
				}

				// done

				didXDIAddress = XdiService.XDIAddressFromDidString(did);

				LOG.info("Set URI in Sovrin: " + uri);
			} catch (Exception ex) {

				throw new RuntimeException("Cannot create DID in Sovrin: " + ex.getMessage(), ex);
			}
		}

		// prepare XDI request

		XDIAddress profileNameXDIAddress = XdiService.XDIAddressFromProfileName(profile.name);
		XDIAddress peopleFinderXDIAddress = XDIAddress.create("+!:did:sov:VpumqBbcVi86RvpEo8lvOn");
		Graph resultGraph;

		// XDI request to local messaging container

		try {

			MessagingContainer messagingContainer = XdiService.get().myLocalMessagingContainer(profile);
			MessageEnvelope messageEnvelope = new MessageEnvelope();
			Message message = messageEnvelope.createMessage(didXDIAddress, -1);
			message.createGetOperation(XDIAddressUtil.concatXDIAddresses(didXDIAddress, XDIAddress.create("#dime#profile"), XDIAddress.create("[<#tag>]")));

			XDILocalClient client = new XDILocalClient(messagingContainer);
			resultGraph = client.send(messageEnvelope).getResultGraph();
		} catch (Xdi2ClientException ex) {

			LOG.error("Cannot execute local XDI message: " + ex.getMessage(), ex);
			return new ResponseEntity(HttpStatus.INTERNAL_SERVER_ERROR);
		}

		// XDI request to People Finder

		try {

			MessageEnvelope messageEnvelope = new MessageEnvelope();
			Message message1 = messageEnvelope.createMessage(didXDIAddress, -1);
			message1.setFromXDIAddress(didXDIAddress);
			message1.setToXDIAddress(peopleFinderXDIAddress);
			message1.createDelOperation(didXDIAddress);
			Message message2 = messageEnvelope.createMessage(didXDIAddress, -1);
			message2.setFromXDIAddress(didXDIAddress);
			message2.setToXDIAddress(peopleFinderXDIAddress);
			message2.createSetOperation(resultGraph);

			XDIHttpClient client = new XDIHttpClient(dimeConfig.getPeoplefinderEndpoint());
			client.send(messageEnvelope);
			client.close();
		} catch (Xdi2ClientException ex) {

			LOG.error("Cannot send XDI message to People Finder: " + ex.getMessage(), ex);
			return new ResponseEntity(HttpStatus.INTERNAL_SERVER_ERROR);
		}

		// On success

		return new ResponseEntity(HttpStatus.NO_CONTENT);
	}


	@Transactional(readOnly=true)
	@Scheduled(initialDelay=30000, fixedRate=60000)
	public void updateSearchIndex() {
		LOG.debug("Scheduled checking of Lucene index.");
		searchIndex.updateIndex();        
	}

	/**
       Helper method to transform the search results into an
       appropriate format for returning from the API.
	 */

	protected SearchResults doSearch(SearchQuery query, String className,
			String typeName, int limit, User user,
			WeightType termWeighting, boolean updateIndex)
					throws IOException, SearchQueryException
	{
		if (query.isEmpty())
			return new SearchResults();

		if (updateIndex)
			searchIndex.updateIndex();

		SearchResults res = searchIndex.search(query, className, typeName,
				limit, user.getId(),
				termWeighting);
		searchIndex.mapToElements(res);

		LOG.info("Search query \"{}\" (limit={}) returned {} results.",
				query, limit, res.getNumFound());
		return res;
	}

	/**
       Helper method to transform the information element search
       results into their corresponding events for returning from the
       API.
	 */

	protected SearchResults doEventSearch(SearchQuery query, String className,
			String typeName, int limit, User user,
			WeightType termWeighting, boolean updateIndex)
					throws IOException, SearchQueryException
	{
		if (query.isEmpty())
			return new SearchResults();

		if (updateIndex)
			searchIndex.updateIndex();

		SearchResults res = searchIndex.search(query, className, typeName,
				limit, user.getId(),
				termWeighting);
		searchIndex.mapToEvents(res, user);

		LOG.info("Search query \"{}\" (limit={}) returned {} results.",
				query, limit, res.getNumFound());

		return res;
	}

	/**
       @apiDefine user User access 
       You need to be authenticated as a registered DiMe user.
	 */

	/** HTTP end point for uploading a single event. 
        @api {get} /search Information element search
        @apiName SearchInformationElement
        @apiDescription Perform a text search on existing information elements in DiMe. The search is performed using Lucene in the DiMe backend.

It returns an object that contains some meta-data and in the "docs" element a list of InformationElement objects together with a score indicating the relevance of the object to the search query. The list is sorted by this score, descending.

        @apiParam {Number} query Query text to search for

        @apiParam (Options) {Number} [limit] limit the number of results
        @apiParam (Options) {Boolean} [includeTerms] set to "true" in order to include indexing terms
        @apiParam (Options) {Boolean} [updateIndex] set to "true" to force an index update before the search

        @apiSuccessExample {json} Example successful response:
            HTTP/1.1 200 OK
            {
              "docs": [
                {
                  "plainTextContent": "Some text content\n",
                  "user": {
                    "id": "5524d8ede4b06e42cc0e0aca",
                    "role": "USER",
                    "username": "testuser"
                  },
                  "uri": "file:///home/testuser/some_file.txt",
                  "type": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#TextDocument",
                  "mimeType": "text/plain",
                  "timeCreated": 1430142736819,
                  "id": "d8b5b874e4bae5a6f6260e1042281e91c69d305e",
                  "timeModified": 1430142736819,
                  "score": 0.75627613,
                  "isStoredAs": "http://www.semanticdesktop.org/ontologies/nfo#FileDataObject"
                },
                {
                  "plainTextContent": "Some other text content",
                  "user": {
                    "id": "5524d8ede4b06e42cc0e0aca",
                    "role": "USER",
                    "username": "testuser"
                  },
                  "uri": "file:///home/testuser/another_file.txt",
                  "type": "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#TextDocument",
                  "mimeType": "text/plain",
                  "timeCreated": 1430142737246,
                  "id": "99db4832be27cff6b08a1f91afbf0401cad49d15",
                  "timeModified": 1430142737246,
                  "score": 0.75342464,
                  "isStoredAs": "http://www.semanticdesktop.org/ontologies/nfo#FileDataObject"
                }
              ],
              "numFound": 2
            }

        @apiErrorExample {json} Example error response for erroneous Lucene query:
            HTTP/1.1 400 OK
            {
              "docs": [],
              "message": "Syntax Error, cannot parse a::  ",
              "numFound": 0
            }

        @apiPermission user
        @apiGroup Search
        @apiVersion 0.1.2
	 */
	@RequestMapping(value="/search", method = RequestMethod.GET)
	public ResponseEntity<SearchResults>
	search(Authentication auth,
			@RequestParam String query,
			@RequestParam(value="@type", required=false) String className,
			@RequestParam(value="type", required=false) String typeName,
			@RequestParam(value="includeTerms", required=false, 
			defaultValue="") String includeTerms,
			@RequestParam(defaultValue="-1") int limit,
			@RequestParam(defaultValue="false") boolean updateIndex)
	{
		User user = getUser(auth);

		try {
			TextSearchQuery textQuery = new TextSearchQuery(query);
			SearchResults results = doSearch(textQuery, className, typeName, limit, user, 
					weightType(includeTerms), updateIndex);

			return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
		} catch (IOException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.INTERNAL_SERVER_ERROR);
		} catch (SearchQueryException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.BAD_REQUEST);
		}
	}

	/**
        @api {get} /eventsearch Event search
        @apiName SearchEvent
        @apiDescription Perform a text search on existing events in
        DiMe. Most events do not contain any text content by
        themselves, and for these the search is actually performed
        against the information element objects they are linked to. For
        example if a document matches the search, all the events which
        refer to the object are returned. The search is performed
        using Lucene in the DiMe backend.

The end point returns a JSON list of event objects with their linked
        information element object included. Note: since the
        information elements may be repeated several times in the
        results and their text content very long, their
        plainTextContent field has been removed. (It can be fetched
        separately by id.)

The return format is the same as for the <a href="#api-Search-SearchInformationElement">information element search</a>.

        @apiParam {Number} query Query text to search for

        @apiParam (Options) {Number} [limit] limit the number of results
        @apiParam (Options) {Boolean} [includeTerms] set to "true" in order to include indexing terms
        @apiParam (Options) {Boolean} [updateIndex] set to "true" to force an index update before the search

        @apiPermission user
        @apiGroup Search
        @apiVersion 0.1.2
	 */
	@RequestMapping(value="/eventsearch", method = RequestMethod.GET)
	public ResponseEntity<SearchResults>
	eventSearch(Authentication auth,
			@RequestParam String query,
			@RequestParam(value="@type", required=false) String className,
			@RequestParam(value="type", required=false) String typeName,
			@RequestParam(value="includeTerms", required=false,
			defaultValue="") String includeTerms,
			@RequestParam(defaultValue="-1") int limit,
			@RequestParam(defaultValue="false") boolean updateIndex) {
		User user = getUser(auth);

		try {
			TextSearchQuery textQuery = new TextSearchQuery(query);
			SearchResults results = doEventSearch(textQuery, className, typeName, limit, user,
					weightType(includeTerms), updateIndex);

			return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
		} catch (IOException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.INTERNAL_SERVER_ERROR);
		} catch (SearchQueryException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.BAD_REQUEST);
		}
	}

	/**
        @api {post} /keywordsearch 
        @apiName KeywordSearch
        @apiDescription Perform an information element search based on
        the POSTed weighted keywords.

        @apiPermission user
        @apiGroup Search
        @apiVersion 0.1.2
	 */
	@RequestMapping(value="/keywordsearch", method = RequestMethod.POST)
	public ResponseEntity<SearchResults>
	search(Authentication auth, @RequestBody WeightedKeyword[] input) 
	{
		User user = getUser(auth);

		try {
			KeywordSearchQuery query = new KeywordSearchQuery(input);
			SearchResults results = doSearch(query, null, null,  -1, user, 
					WeightType.Tf, true);
			return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
		} catch (IOException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.INTERNAL_SERVER_ERROR);
		} catch (SearchQueryException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.BAD_REQUEST);
		}
	}

	/**
        @api {post} /eventkeywordsearch 
        @apiName EventKeywordSearch
        @apiDescription Perform an event search based on the POSTed weighted keywords.

        @apiPermission user
        @apiGroup Search
        @apiVersion 0.1.2
	 */
	@RequestMapping(value="/eventkeywordsearch", method = RequestMethod.POST)
	public ResponseEntity<SearchResults>
	eventSearch(Authentication auth, @RequestBody WeightedKeyword[] input) 
	{
		User user = getUser(auth);

		try {
			KeywordSearchQuery query = new KeywordSearchQuery(input);
			SearchResults results = doEventSearch(query, null, null, -1, user, 
					WeightType.Tf, true);

			return new ResponseEntity<SearchResults>(results, HttpStatus.OK);
		} catch (IOException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.INTERNAL_SERVER_ERROR);
		} catch (SearchQueryException e) {
			return new ResponseEntity<SearchResults>
			(new SearchResults(e.getMessage()),
					HttpStatus.BAD_REQUEST);
		}
	}
}
