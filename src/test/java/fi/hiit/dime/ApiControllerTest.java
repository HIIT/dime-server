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

import static org.junit.Assert.*;
import static fi.hiit.dime.data.DiMeData.makeStub;

import fi.hiit.dime.ApiController.ApiMessage;
import fi.hiit.dime.data.DiMeData;
import fi.hiit.dime.data.Document;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.EventRelation;
import fi.hiit.dime.data.FeedbackEvent;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.InformationElementRelation;
import fi.hiit.dime.data.IntentModelFeedbackEvent;
import fi.hiit.dime.data.Message;
import fi.hiit.dime.data.MessageEvent;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.data.ReadingEvent;
import fi.hiit.dime.data.ResourcedEvent;
import fi.hiit.dime.data.ScientificDocument;
import fi.hiit.dime.data.SearchEvent;
import fi.hiit.dime.data.Tag;
import fi.hiit.dime.search.KeywordSearchQuery;
import fi.hiit.dime.search.SearchIndex;
import fi.hiit.dime.search.SearchResults;
import fi.hiit.dime.util.RandomPassword;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
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
        SearchResults res = doSearch("");

        assertEquals(0, res.getDocs().size());
    }

    private SearchResults doSearch(String query) {
        return getData(apiUrl("/search?updateIndex=true&query=" + query), SearchResults.class);
    }

    private SearchResults doEventSearch(String query) {
        return getData(apiUrl("/eventsearch?updateIndex=true&query=" + query),
                       SearchResults.class);
    }

    @Test
    public void testSearch() throws Exception {
        final String magicWord = "foobar";

        // Search without events should return zero
        SearchResults searchResEmpty = doSearch(magicWord);
        assertEquals(0, searchResEmpty.getDocs().size());

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
        extraEvent.targettedResource =
            ((MessageEvent)events[5]).targettedResource;

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
                idToFind.add(((MessageEvent)uploadedEvents[i]).
                             targettedResource.getId());
        }

        // Now try searching for the ones in idxToFind
        SearchResults searchRes = doSearch(magicWord+"&@type=Message");

        dumpData("searchRes", searchRes);

        // Check that we have the expected number of results
        assertEquals(idxToFind.size(), searchRes.getDocs().size());
        assertEquals(idxToFind.size(), searchRes.getNumFound());

        Set<Long> idFound = new HashSet<Long>();
        for (DiMeData data : searchRes.getDocs()) {
            assertTrue(data instanceof InformationElement);
            InformationElement elem = (InformationElement)data;
            // Check that each returned document contains the expected word
            assertTrue(elem.plainTextContent.contains(magicWord));
            idFound.add(elem.getId());

            assertTrue(elem.hasTags());
        }

        // Check that the ids are exactly those expected
        assertEquals(idToFind, idFound);

        // Try searching as events
        SearchResults searchEventsRes =
            doEventSearch(magicWord+"&@type=Message");

        dumpData("searchEventsRes", searchEventsRes);

        // Check that we have the expected number of results
        // +1 because we added a last event with duplicate msg
        assertEquals(idxToFind.size()+1, searchEventsRes.getDocs().size());

        Set<Long> idFound2 = new HashSet<Long>();
        for (DiMeData data : searchEventsRes.getDocs()) {
            assertTrue(data instanceof ResourcedEvent);

            ResourcedEvent revent = (ResourcedEvent)data;

            idFound2.add(revent.targettedResource.getId());
        }

        // Check that the ids are exactly those expected
        assertEquals(idToFind, idFound2);

        // Search for SearchEvents only
        SearchResults searchByTypeRes =
            doEventSearch("foobar&@type=SearchEvent");

        assertEquals(1, searchByTypeRes.getDocs().size());
        DiMeData obj = searchByTypeRes.getDocs().get(0);
        assertEquals(searchEvent.appId, obj.appId);
        assertTrue(obj instanceof SearchEvent);
        assertEquals(searchEvent.query, ((SearchEvent)obj).query);

        ApiError error = getDataExpectError(apiUrl("/search?query=a:"));
    }

    @Test
    public void testReadingEventSearch() throws Exception {
        String magicText = "foobarbaz";
        ScientificDocument doc = createScientificDocument(randomText);
        ReadingEvent re = createReadingEvent(doc, magicText);
        re.appId = "hgfewiuhoi543rughierh";

        uploadEvent(re, ReadingEvent.class);

        SearchResults searchEventsRes = doEventSearch(magicText);

        dumpData("searchEventsRes", searchEventsRes);

        assertEquals(1, searchEventsRes.getDocs().size());
        assertEquals(1, searchEventsRes.getNumFound());

        assertTrue(searchEventsRes.getDocs().get(0) instanceof ReadingEvent);

        ReadingEvent res = (ReadingEvent)searchEventsRes.getDocs().get(0);

        assertEquals(re.appId, res.appId);
        assertEquals(re.plainTextContent, res.plainTextContent);

        // Because we are nulling the document content
        assertEquals(null, res.targettedResource.plainTextContent);


        // Try searching on InformationElements
        SearchResults searchRes = doSearch(magicText);
        dumpData("reading events via InformationElements search", searchRes);

        assertEquals(1, searchRes.getDocs().size());
        assertEquals(1, searchRes.getNumFound());

        assertTrue(searchRes.getDocs().get(0) instanceof ScientificDocument);

        ScientificDocument docRes = (ScientificDocument)searchRes.getDocs().get(0);

        assertEquals(docRes.plainTextContent, docRes.plainTextContent);

        assertEquals(docRes.eventTime, res.start);
        
    }

    @Test
    public void testKeywordSearch() throws Exception {
        String magicText = "foobarbaz";
        ScientificDocument doc = createScientificDocument(randomText);
        ReadingEvent re = createReadingEvent(doc, magicText);
        re.appId = "hgfewiuhoi543rughierh";

        uploadEvent(re, ReadingEvent.class);

        KeywordSearchQuery query1 = new KeywordSearchQuery();
        query1.add("foobarbaz", 0.4f);
        query1.add("tellus", 0.1f);

        dumpData("query", query1);
        SearchResults resEvents = uploadData(apiUrl("/eventkeywordsearch?updateIndex=true"),
                                             query1.weightedKeywords,
                                             SearchResults.class);

        dumpData("keyword search results (events)", resEvents);
        assertEquals(1, resEvents.getDocs().size());
        assertEquals(1, resEvents.getNumFound());
        assertEquals(query1.weightedKeywords, resEvents.queryTerms);

        KeywordSearchQuery query2 = new KeywordSearchQuery();
        query2.add("foobarbaz", 0.4f);
        SearchResults resElems = uploadData(apiUrl("/keywordsearch"),
                                       query2.weightedKeywords,
                                       SearchResults.class);

        dumpData("keyword search results (elems)", resElems);
        assertEquals(1, resElems.getDocs().size());
        assertEquals(1, resElems.getNumFound());
        assertEquals(query2.weightedKeywords, resElems.queryTerms);

        assertTrue(resElems.getDocs().get(0) instanceof ScientificDocument);
        ScientificDocument resDoc = (ScientificDocument)resElems.getDocs().get(0);
        assertTrue(resDoc.weightedKeywords != null);
        assertTrue(resDoc.weightedKeywords.size() > 0);

        // Read back uploaded document
        ScientificDocument getDoc1 = getData(infoElemApi + "/" + resDoc.getId(),
                                            ScientificDocument.class);
        assertEquals(getDoc1.plainTextContent, doc.plainTextContent);
        assertTrue(getDoc1.weightedKeywords == null);

        ScientificDocument getDoc2 = getData(infoElemApi + "/" + resDoc.getId() +
                                             "?keywords=true",
                                            ScientificDocument.class);
        assertEquals(getDoc2.plainTextContent, doc.plainTextContent);
        assertTrue(getDoc2.weightedKeywords != null);
        assertEquals(55, getDoc2.weightedKeywords.size());

        System.out.println(getDoc2.weightedKeywords.size());
    }

    @Test
    public void testProfiles() throws Exception {
        // Create a document
        Document doc = new Document();
        doc.uri = "http://www.example.com/hello68.txt";
        doc.plainTextContent = "Hello, world";
        doc.mimeType = "text/plain";

        // Create feedback, with document embedded
        FeedbackEvent event1 = new FeedbackEvent();
        event1.value = 0.68;
        event1.targettedResource = doc;

        FeedbackEvent outEvent1 = uploadEvent(event1, FeedbackEvent.class);

        // Test uploading a new profile
        Profile profile = new Profile("Kai's formula profile");
        profile.tags.add(new Tag("Formula1"));
        profile.tags.add(new Tag("motorsports"));
        profile.addEvent(makeStub(outEvent1, FeedbackEvent.class), 0.9, "UnitTest");
        profile.addInformationElement(makeStub((Document)outEvent1.targettedResource, 
                                               Document.class), 0.8, "UnitTest");
        
        dumpData("profile before", profile);
        Profile uploadedProfile = uploadData(profileApi, profile,
                                             Profile.class);
        dumpData("uploadedProfile", uploadedProfile);

        assertEquals(profile.name, uploadedProfile.name);
        assertEquals(profile.tags.size(), uploadedProfile.tags.size());
        Long id = uploadedProfile.getId();
        assertTrue(id != null && id > 0);

        assertEquals(1, uploadedProfile.suggestedEvents.size());
        assertEquals(0, uploadedProfile.validatedEvents.size());
        assertEquals(1, uploadedProfile.suggestedInformationElements.size());
        assertEquals(0, uploadedProfile.validatedInformationElements.size());

        Tag newTag = new Tag("kimi raikkonen");
        Tag uploadedTag = uploadData(profileApiUrl(id, "tags"), newTag, Tag.class);

        // Test fetching an existing one
        Profile gotProfile = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile", gotProfile);

        assertEquals(profile.name, gotProfile.name);
        assertEquals(3, gotProfile.tags.size());
        Long gotId = gotProfile.getId();
        assertEquals(id, gotId);

        // Test updating an existing profile
        gotProfile.tags.add(new Tag("f1"));
        gotProfile.name = "Kai's Formula Profile";

        Map<String, Double> intent = new HashMap<String, Double>();
        intent.put("foo", 0.4);
        intent.put("bar", 0.1);
        intent.put("baz", 0.99);
        gotProfile.intent = intent;

        Profile updatedProfile = uploadData(profileApi, gotProfile,
                                            Profile.class);
        assertEquals(id, updatedProfile.getId());
        assertEquals(updatedProfile.name, gotProfile.name);
        
        // Test fetching the updated one
        Profile gotUpdatedProfile = getData(profileApiUrl(id), Profile.class);
        dumpData("gotUpdatedProfile", gotUpdatedProfile);

        assertEquals(gotProfile.name, gotUpdatedProfile.name);
        assertEquals(gotProfile.tags.size(), gotUpdatedProfile.tags.size());
        Long gotUpdatedId = gotUpdatedProfile.getId();
        assertEquals(id, gotUpdatedId);
        assertEquals(3, gotUpdatedProfile.intent.size());
        assertTrue(gotUpdatedProfile.intent.equals(intent));

        deleteData(profileApiUrl(id, "tags", uploadedTag.getId()));

        Tag[] tagList = getData(profileApiUrl(id, "tags"), Tag[].class);
        assertEquals(gotProfile.tags.size()-1, tagList.length);

        // Create a document
        Document doc1 = new Document();
        doc1.uri = "http://www.example.com/hello2.txt";
        doc1.plainTextContent = "Hello, world";
        doc1.mimeType = "text/plain";

        // Create feedback, with document embedded
        FeedbackEvent event2 = new FeedbackEvent();
        event2.value = 0.22;
        event2.targettedResource = doc1;

        FeedbackEvent outEvent2 = uploadEvent(event2, FeedbackEvent.class);

        // Test adding a suggested event
        EventRelation eventSuggestion = new EventRelation(outEvent2, 0.42, "UnitTest");
        dumpData("eventSuggestion", eventSuggestion);
        EventRelation suggestedEvent = uploadData(profileApiUrl(id, "suggestedevents"),
                                                  eventSuggestion, EventRelation.class);

        Profile gotProfile2 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile2", gotProfile2);
        assertEquals(2, gotProfile2.suggestedEvents.size());
        assertEquals(0, gotProfile2.validatedEvents.size());
        assertEquals(1, gotProfile2.suggestedInformationElements.size());
        assertEquals(0, gotProfile2.validatedInformationElements.size());

        // Test adding a suggested non-existent event
        EventRelation eventSuggestionBad = new EventRelation(event2, 0.42, "UnitTest");
        uploadData(profileApiUrl(id, "suggestedevents"), eventSuggestionBad, ApiError.class);

        Profile gotProfile3 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile3", gotProfile3);
        assertEquals(2, gotProfile3.suggestedEvents.size());
        assertEquals(0, gotProfile3.validatedEvents.size());
        assertEquals(1, gotProfile3.suggestedInformationElements.size());
        assertEquals(0, gotProfile3.validatedInformationElements.size());

        // Test validating an event
        EventRelation eventValidation = new EventRelation(outEvent2, 0.90, "UnitTest");
        EventRelation validatedEvent = uploadData(profileApiUrl(id, "validatedevents"),
                                                  eventValidation, EventRelation.class);

        dumpData("validatedEvent", validatedEvent);

        Profile gotProfile4 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile4", gotProfile4);
        assertEquals(2, gotProfile4.suggestedEvents.size());
        assertEquals(1, gotProfile4.validatedEvents.size());
        assertEquals(1, gotProfile4.suggestedInformationElements.size());
        assertEquals(0, gotProfile4.validatedInformationElements.size());

        // Check that the corresponding event in suggested events also was updated.
        assertTrue(gotProfile4.validatedEvents.get(0).validated);
        assertTrue(gotProfile4.suggestedEvents.get(1).validated);

        // Test adding a suggested information element
        Document doc2 = new Document();
        doc2.uri = "http://www.example.com/formula.txt";
        doc2.plainTextContent = "Formula something something";
        doc2.mimeType = "text/plain";

        Document outDoc2 = uploadElement(doc2, Document.class);

        InformationElementRelation elemSuggestion = 
            new InformationElementRelation(outDoc2, 0.99, "UnitTest");
        InformationElementRelation suggestedElem = 
            uploadData(profileApiUrl(id, "suggestedinformationelements"), elemSuggestion, 
                       InformationElementRelation.class);

        Profile gotProfile5 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile5", gotProfile5);
        assertEquals(2, gotProfile5.suggestedEvents.size());
        assertEquals(1, gotProfile5.validatedEvents.size());
        assertEquals(2, gotProfile5.suggestedInformationElements.size());
        assertEquals(0, gotProfile5.validatedInformationElements.size());

        // Test validating new element
        Document doc3 = new Document();
        doc3.uri = "http://www.example.com/formula1.txt";
        doc3.plainTextContent = "Formula 1 something something";
        doc3.mimeType = "text/plain";

        Document outDoc3 = uploadElement(doc3, Document.class);

        InformationElementRelation elemValidation = 
            new InformationElementRelation(outDoc3, 0.43, "UnitTest");
        uploadData(profileApiUrl(id, "validatedinformationelements"), elemValidation, 
                   InformationElementRelation.class);

        Profile gotProfile6 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile6", gotProfile6);
        assertEquals(2, gotProfile6.suggestedEvents.size());
        assertEquals(1, gotProfile6.validatedEvents.size());
        assertEquals(2, gotProfile6.suggestedInformationElements.size());
        assertEquals(1, gotProfile6.validatedInformationElements.size());

        assertTrue(gotProfile6.validatedInformationElements.get(0).validated);
        assertFalse(gotProfile6.suggestedInformationElements.get(1).validated);

        // Test validating previously suggested element
        InformationElementRelation elemValidation2 = 
            new InformationElementRelation(outDoc2, 0.88, "UnitTest");
        dumpData("about to validate", elemValidation2);
        uploadData(profileApiUrl(id, "validatedinformationelements"), elemValidation2, 
                   InformationElementRelation.class);

        Profile gotProfile7 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile7", gotProfile7);
        assertEquals(2, gotProfile7.suggestedEvents.size());
        assertEquals(1, gotProfile7.validatedEvents.size());
        assertEquals(2, gotProfile7.suggestedInformationElements.size());
        assertEquals(2, gotProfile7.validatedInformationElements.size());

        assertTrue(gotProfile7.validatedInformationElements.get(0).validated);
        assertTrue(gotProfile7.validatedInformationElements.get(1).validated);
        assertTrue(gotProfile7.suggestedInformationElements.get(1).validated);

        // Test re-validating previously validated element
        InformationElementRelation elemValidation3 = 
            new InformationElementRelation(outDoc2, 0.99, "UnitTest");
        InformationElementRelation validatedElem =
            uploadData(profileApiUrl(id, "validatedinformationelements"), elemValidation3, 
                       InformationElementRelation.class);

        Profile gotProfile8 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile8", gotProfile8);
        assertEquals(2, gotProfile8.suggestedEvents.size());
        assertEquals(1, gotProfile8.validatedEvents.size());
        assertEquals(2, gotProfile8.suggestedInformationElements.size());
        assertEquals(2, gotProfile8.validatedInformationElements.size());
        assertEquals(0.99, gotProfile8.validatedInformationElements.get(1).weight, 0.0001);

        assertTrue(gotProfile8.validatedInformationElements.get(0).validated);
        assertTrue(gotProfile8.validatedInformationElements.get(1).validated);
        assertTrue(gotProfile8.suggestedInformationElements.get(1).validated);

        // Test direct GET requests on the profile's lists 
        EventRelation[] resSuggestedEvents = getData(profileApiUrl(id, "suggestedevents"),
                                                     EventRelation[].class);
        assertEquals(2, resSuggestedEvents.length);

        EventRelation[] resValidatedEvents = getData(profileApiUrl(id, "validatedevents"),
                                                     EventRelation[].class);
        assertEquals(1, resValidatedEvents.length);

        InformationElementRelation[] resSuggestedElems = 
            getData(profileApiUrl(id, "suggestedinformationelements"),
                    InformationElementRelation[].class);
        assertEquals(2, resSuggestedElems.length);

        InformationElementRelation[] resValidatedElems = 
            getData(profileApiUrl(id, "validatedinformationelements"),
                    InformationElementRelation[].class);
        assertEquals(2, resValidatedElems.length);

        // Test deleting validated infoelem
        deleteData(profileApiUrl(id, "validatedinformationelements", validatedElem.getId()));

        Profile gotProfile9 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile9", gotProfile9);
        assertEquals(2, gotProfile9.suggestedInformationElements.size());
        assertEquals(1, gotProfile9.validatedInformationElements.size());
        assertFalse(gotProfile9.suggestedInformationElements.get(1).validated);

        // Test deleting suggested infoelem
        deleteData(profileApiUrl(id, "suggestedinformationelements", suggestedElem.getId()));

        Profile gotProfile10 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile10", gotProfile10);
        assertEquals(1, gotProfile10.suggestedInformationElements.size());
        assertEquals(1, gotProfile10.validatedInformationElements.size());

        // Test deleting validated event
        deleteData(profileApi + "/" + id + "/validatedevents/" + 
                   validatedEvent.getId());

        Profile gotProfile11 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile11", gotProfile11);
        assertEquals(2, gotProfile11.suggestedEvents.size());
        assertEquals(0, gotProfile11.validatedEvents.size());
        assertFalse(gotProfile11.suggestedEvents.get(0).validated);

        // Test deleting suggested event
        deleteData(profileApiUrl(id, "suggestedevents", suggestedEvent.getId()));

        Profile gotProfile12 = getData(profileApiUrl(id), Profile.class);
        dumpData("gotProfile12", gotProfile10);
        assertEquals(1, gotProfile12.suggestedEvents.size());
        assertEquals(0, gotProfile12.validatedEvents.size());

        // Try fetching a random non-existing profile
        getDataExpectError(profileApi + "/129382190");

        Profile[] profiles = getData(apiUrl("/profiles"), Profile[].class);
        assertEquals(1, profiles.length);
        assertEquals(profiles[0].getId(), updatedProfile.getId());
        assertEquals(profiles[0].name, updatedProfile.name);

        // Test deleting profile
        deleteData(profileApiUrl(id));
        getDataExpectError(profileApiUrl(id));
    }

    @Test
    public void testIntentModelFeedback() throws Exception {
        Profile profile = new Profile("Some profile");
        Map<String, Double> intent = new HashMap<String, Double>();
        intent.put("foo", 0.4);
        intent.put("bar", 0.1);
        intent.put("baz", 0.99);
        profile.intent = intent;

        Profile uploadedProfile = uploadData(profileApi, profile, Profile.class);
        uploadedProfile.name = "Some profile2";

        Profile stubProfile = Profile.makeStub(uploadedProfile);

        IntentModelFeedbackEvent event = new IntentModelFeedbackEvent();
        event.relatedProfile = stubProfile;
        event.intent = intent;
        event.weight = 0.42;

        dumpData("IntentModelFeedbackEvent before upload", event);

        IntentModelFeedbackEvent uploadedEvent = uploadData(eventApi, event,
                                                            IntentModelFeedbackEvent.class);
        dumpData("IntentModelFeedbackEvent after upload", uploadedEvent);
    }
}
