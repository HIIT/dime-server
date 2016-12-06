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

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.DiMeData;
import fi.hiit.dime.data.DiMeDataRelation;
import fi.hiit.dime.data.Event;
import fi.hiit.dime.data.EventRelation;
import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.data.InformationElementRelation;
import fi.hiit.dime.data.Profile;
import fi.hiit.dime.data.Tag;
import fi.hiit.dime.database.EventDAO;
import fi.hiit.dime.database.InformationElementDAO;
import fi.hiit.dime.database.ProfileDAO;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.InvalidDataAccessApiUsageException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

/**
 * Profiles API controller.
 *
 * @author Mats Sjöberg, mats.sjoberg@helsinki.fi
 */
@RestController
@RequestMapping("/api/profiles")
public class ProfilesController extends AuthorizedController {
    private static final Logger LOG =
        LoggerFactory.getLogger(ProfilesController.class);

    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;
    private final ProfileDAO profileDAO;

    @Autowired 
    private ObjectMapper objectMapper;

    @Autowired
    ProfilesController(EventDAO eventDAO,
                  InformationElementDAO infoElemDAO,
                  ProfileDAO profileDAO) {
        this.eventDAO = eventDAO;
        this.infoElemDAO = infoElemDAO;
        this.profileDAO = profileDAO;
    }

    /**
     * Helper method to save a profile.
     *
     * @param input Profile to store
     * @param user current authenticated user
     * @return The profile as stored
     */
    @Transactional
    private Profile storeProfile(Profile profile, User user) {
        profile.user = user;
        profileDAO.save(profile);

        return profile;
    }

    private void addEventRelation(Profile profile, EventRelation relation, boolean validated,
                                  User user) 
        throws NotFoundException
    {
        Event event = eventDAO.findById(relation.event.getId());
                
        if (event == null || !event.user.getId().equals(user.getId()))
            throw new NotFoundException("Event not found");
 
        relation.event = event;
            
        if (validated) 
            profile.validateEvent(relation);
        else
            profile.addEvent(relation);
    }

    private void addInformationElementRelation(Profile profile, InformationElementRelation relation,
                                               boolean validated, User user) 
        throws NotFoundException
    {
        InformationElement elem = infoElemDAO.findById(relation.informationElement.getId());
            
        if (elem == null || !elem.user.getId().equals(user.getId()))
            throw new NotFoundException("InformationElement not found");
            
        relation.informationElement = elem;
        
        if (validated)
            profile.validateInformationElement(relation);
        else
            profile.addInformationElement(relation);
    }

    /**
     * Helper method to update profile with EventRelation.
     *
     * @param profileId Id of the profile to update
     * @param relation The EventRelation to add to the profile
     * @param validated True if the relation is a "validation" relation, otherwise it is "suggested"
     * @param user current authenticated user
     */
    @Transactional
    private EventRelation updateProfile(Long profileId, EventRelation relation, boolean validated,
                                        User user) 
        throws NotFoundException, BadRequestException
    {
        try {
            Profile profile = getProfile(profileId, user);

            addEventRelation(profile, relation, validated, user);

            profile = storeProfile(profile, user);

            if (validated)
                return profile.findValidatedEvent(relation);
            else
                return profile.findSuggestedEvent(relation);

        } catch (IllegalArgumentException | InvalidDataAccessApiUsageException e) {
            throw new BadRequestException("Invalid argument: " + relation);
        }
    }

    /**
     * Helper method to update profile with InformationElementRelation.
     *
     * @param profileId Id of the profile to update
     * @param relation The InformationElementRelation to add to the profile
     * @param validated True if the relation is a "validation" relation, otherwise it is "suggested"
     * @param user current authenticated user
     */
    @Transactional
    private InformationElementRelation updateProfile(Long profileId,
                                                     InformationElementRelation relation, 
                                                     boolean validated, User user) 
        throws NotFoundException, BadRequestException
    {
        try {
            Profile profile = getProfile(profileId, user);

            addInformationElementRelation(profile, relation, validated, user);

            profile = storeProfile(profile, user);

            if (validated)
                return profile.findValidatedInformationElement(relation);
            else
                return profile.findSuggestedInformationElement(relation);

        } catch (IllegalArgumentException | InvalidDataAccessApiUsageException e) {
            throw new BadRequestException("Invalid argument: " + relation);
        }
    }

    private Profile getProfile(Long profileId, User user) 
        throws NotFoundException 
    {
        Profile profile = profileDAO.findById(profileId, user);
        
        if (profile == null || !profile.user.getId().equals(user.getId()))
            throw new NotFoundException("Profile not found");
        return profile;
    }

    @Transactional
    private void deleteProfileInformationElementRelation(Long profileId, Long relationId, 
                                                         boolean validated, User user) 
        throws NotFoundException
    {
        Profile profile = getProfile(profileId, user);

        InformationElementRelation relation = null;
        if (validated)
            relation = profile.findValidatedInformationElement(relationId);
        else
            relation = profile.findSuggestedInformationElement(relationId);

        if (relation == null)
            throw new NotFoundException("Relation not found");

        if (validated)
            profile.removeValidatedInformationElement(relation);
        else
            profile.removeInformationElement(relation);

        storeProfile(profile, user);
    }

    @Transactional
    private void deleteProfileEventRelation(Long profileId, Long relationId, 
                                            boolean validated, User user) 
        throws NotFoundException
    {
        Profile profile = getProfile(profileId, user); 

        EventRelation relation = null;
        if (validated)
            relation = profile.findValidatedEvent(relationId);
        else
            relation = profile.findSuggestedEvent(relationId);

        if (relation == null)
            throw new NotFoundException("Relation not found");

        if (validated)
            profile.removeValidatedEvent(relation);
        else
            profile.removeEvent(relation);

        storeProfile(profile, user);
    }

    //--------------------------------------------------------------------------

    private void resetEventRelations(Profile profile, List<EventRelation> rels, boolean validated,
                                     User user) 
        throws NotFoundException 
    {
        List<EventRelation> tempList = new ArrayList<EventRelation>(rels);
        rels.clear();
        for (EventRelation r : tempList) addEventRelation(profile, r, validated, user);
    }

    private void resetInformationElementRelations(Profile profile, 
                                                  List<InformationElementRelation> rels, 
                                                  boolean validated, User user) 
        throws NotFoundException 
    {
        List<InformationElementRelation> tempList = new ArrayList<InformationElementRelation>(rels);
        rels.clear();
        for (InformationElementRelation r : tempList) 
            addInformationElementRelation(profile, r, validated, user);
    }

    /** HTTP end point for creating a new profile. 
        @api {post} /profiles Create or modify a profile
        @apiName Post
        @apiDescription Create a new profile.  If the "id" field is supplied, it will instead update an existing profile. The complete description of the profile data type see the <a href="http://www.hiit.fi/g/reknow/javadoc/dime-server/fi/hiit/dime/data/Profile.html">JavaDoc of the Profile class</a>.
        
        @apiExample {json} Example of JSON to upload
            {
              "@type": "Profile",
              name: "Kai's formula profile",
              searchKeywords: ["x", "y" ],
              "tags" : [ {
                  "@type" : "Tag",
                  "text" : "Formula1"
                }, {
                  "@type" : "Tag",
                  "text" : "motorsports"
                } ],
                "suggestedEvents" : [ {
                  "weight" : 0.9,
                  "actor" : "UnitTest",
                  "validated" : false,
                  "event" : {
                    "@type" : "FeedbackEvent",
                    "id" : 2
                  }
                } ]
            }

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
    */
    @RequestMapping(value="", method = RequestMethod.POST)
    public ResponseEntity<Profile> profile(Authentication auth, @RequestBody Profile input)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        resetEventRelations(input, input.suggestedEvents, false, user);
        resetEventRelations(input, input.validatedEvents, true, user);
        resetInformationElementRelations(input, input.suggestedInformationElements, false, user);
        resetInformationElementRelations(input, input.validatedInformationElements, true, user);

        input = storeProfile(input, user);

        return new ResponseEntity<Profile>(input, HttpStatus.OK);
    }   

    /** HTTP end point for accessing a given profile. 
        @api {get} /profiles/:id Access profile
        @apiName Get
        @apiParam {Number} id Profile's unique ID

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.1.2
     */
    @RequestMapping(value="/{id}", method = RequestMethod.GET)
    public ResponseEntity<Profile>
        profile(Authentication auth, @PathVariable Long id) 
        throws NotFoundException
    {
        User user = getUser(auth);

        Profile profile = getProfile(id, user);

        return new ResponseEntity<Profile>(profile, HttpStatus.OK);
    }   

    /** HTTP end point for accessing all profiles.

        @api {get} /profiles Access all profiles
        @apiName GetAll
        @apiDescription Access all profiles.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
    */    
    @RequestMapping(value="", method = RequestMethod.GET)
    public ResponseEntity<Profile[]>
        profiles(Authentication auth) 
        throws BadRequestException
    {
        User user = getUser(auth);
        
        try {
            List<Profile> profiles = profileDAO.profilesForUser(user.getId());

            Profile[] profilesArray = new Profile[profiles.size()];
            profiles.toArray(profilesArray);        

            return new ResponseEntity<Profile[]>(profilesArray, HttpStatus.OK);
        } catch (IllegalArgumentException | InvalidDataAccessApiUsageException e) {
            throw new BadRequestException("Invalid arguments: " + e);
        }
    }


    /** HTTP end point for deleting a profile.         
        
        @api {delete} /profiles/:id Delete profile
        @apiName Delete
        @apiParam {Number} id Profile's unique ID
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
    */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}", method = RequestMethod.DELETE)
    public void profileDelete(Authentication auth, @PathVariable Long id) 
        throws NotFoundException
    {
        User user = getUser(auth);

        if (!profileDAO.remove(id, user))
            throw new NotFoundException("Profile not found");
    }

    //--------------------------------------------------------------------------

    /** @api {post} /profiles/:id/suggestedevents Add suggested event to profile
        @apiName PostSuggestedEvents
        @apiParam {Number} id Profile's unique ID
        @apiExample  {json} Example of JSON to upload
            {
              "event": {
                  "@type": "SearchEvent",
                  "id": 728,
              },
              "weight": 0.5,
              "actor": "FooAlgorithm"
            }

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/suggestedevents", 
                    method = RequestMethod.POST)
    public ResponseEntity<EventRelation>
        profilePostSuggestedEvents(Authentication auth, @PathVariable Long id,
                            @RequestBody EventRelation suggestedRelation)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        EventRelation rel = updateProfile(id, suggestedRelation, false, user);

        return new ResponseEntity<EventRelation>(rel, HttpStatus.OK);
    }

    /** @api {get} /profiles/:id/suggestedevents Get list of suggested events for profile
        @apiName GetSuggestedEvents
        @apiParam {Number} id Profile's unique ID

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/suggestedevents", 
                    method = RequestMethod.GET)
    public ResponseEntity<EventRelation[]>
        profileGetSuggestedEvents(Authentication auth, @PathVariable Long id)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        List<EventRelation> list = getProfile(id, user).suggestedEvents;
        EventRelation[] res = new EventRelation[list.size()];
        list.toArray(res);

        return new ResponseEntity<EventRelation[]>(res, HttpStatus.OK);
    }

    /** @api {delete} /profiles/:id/suggestedevents/:rid Delete suggested event from profile
        @apiName DeleteSuggestedEvents
        @apiParam {Number} id Profile's unique ID
        @apiParam {Number} rid The ID of the validation relation
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}/suggestedevents/{rid}", 
                    method = RequestMethod.DELETE)
    public void profileDeleteSuggestedEvents(Authentication auth, @PathVariable Long id, 
                                             @PathVariable Long rid)
        throws NotFoundException
    {
        User user = getUser(auth);

        deleteProfileEventRelation(id, rid, false, user);
    }   

    //--------------------------------------------------------------------------

    /** @api {post} /profiles/:id/validatedevents Add validated event to profile
        @apiName PostValidatedEvents
        @apiParam {Number} id Profile's unique ID
        @apiExample  {json} Example of JSON to upload
            {
              "event": {
                  "@type": "SearchEvent",
                  "id": 728,
              },
              "weight": 0.9,
            }

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/validatedevents", 
                    method = RequestMethod.POST)
    public ResponseEntity<EventRelation>
        profilePostValidatedEvents(Authentication auth, @PathVariable Long id,
                                   @RequestBody EventRelation validatedRelation)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        EventRelation rel = updateProfile(id, validatedRelation, true, user);

        return new ResponseEntity<EventRelation>(rel, HttpStatus.OK);
    }

    /** @api {get} /profiles/:id/validatedevents Get list of validated events for profile
        @apiName GetValidatedEvents
        @apiParam {Number} id Profile's unique ID

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/validatedevents", 
                    method = RequestMethod.GET)
    public ResponseEntity<EventRelation[]>
        profileGetValidatedEvents(Authentication auth, @PathVariable Long id)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        List<EventRelation> list = getProfile(id, user).validatedEvents;
        EventRelation[] res = new EventRelation[list.size()];
        list.toArray(res);

        return new ResponseEntity<EventRelation[]>(res, HttpStatus.OK);
    }

    /** @api {delete} /profiles/:id/validatedevents/:rid Delete validated event from profile
        @apiName DeleteValidatedEvents
        @apiParam {Number} id Profile's unique ID
        @apiParam {Number} rid The ID of the validation relation
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}/validatedevents/{rid}", 
                    method = RequestMethod.DELETE)
    public void profileDeleteValidatedEvents(Authentication auth, @PathVariable Long id, 
                                             @PathVariable Long rid)
        throws NotFoundException
    {
        User user = getUser(auth);

        deleteProfileEventRelation(id, rid, true, user);
    }   

    //--------------------------------------------------------------------------
    
    /** @api {post} /profiles/:id/suggestedinformationelements Add suggested information element to profile
        @apiName PostSuggestedInformationElements
        @apiParam {Number} id Profile's unique ID
        @apiExample  {json} Example of JSON to upload
            {
              "informationelement": {
                  "@type": "Document",
                  "id": 728,
              },
              "weight": 0.22,
              "actor": "FooAlgorithm"
            }

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/suggestedinformationelements", 
                    method = RequestMethod.POST)
    public ResponseEntity<InformationElementRelation>
        profilePostSuggestedInformationElements(Authentication auth, @PathVariable Long id,
                                                @RequestBody InformationElementRelation suggestedRelation)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        InformationElementRelation rel = updateProfile(id, suggestedRelation, false, user);

        return new ResponseEntity<InformationElementRelation>(rel, HttpStatus.OK);
    }

    /** @api {get} /profiles/:id/suggestedinformationelements Get list of suggested informationelements for profile
        @apiName GetSuggestedInformationElements
        @apiParam {Number} id Profile's unique ID

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/suggestedinformationelements", 
                    method = RequestMethod.GET)
    public ResponseEntity<InformationElementRelation[]>
        profileGetSuggestedInformationElements(Authentication auth, @PathVariable Long id)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        List<InformationElementRelation> list = getProfile(id, user).suggestedInformationElements;
        InformationElementRelation[] res = new InformationElementRelation[list.size()];
        list.toArray(res);

        return new ResponseEntity<InformationElementRelation[]>(res, HttpStatus.OK);
    }

    /** @api {delete} /profiles/:id/suggestedinformationelements/:rid Delete suggested informationelement from profile
        @apiName DeleteSuggestedInformationElements
        @apiParam {Number} id Profile's unique ID
        @apiParam {Number} rid The ID of the validation relation
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}/suggestedinformationelements/{rid}", 
                    method = RequestMethod.DELETE)
    public void profileDeleteSuggestedInformationElements(Authentication auth, 
                                                          @PathVariable Long id, 
                                                          @PathVariable Long rid)
        throws NotFoundException
    {
        User user = getUser(auth);

        deleteProfileInformationElementRelation(id, rid, false, user);
    }   
   
    //--------------------------------------------------------------------------

    /** @api {post} /profiles/:id/validatedinformationelements Add validated informationelement to profile
        @apiName PostValidatedInformationElements
        @apiParam {Number} id Profile's unique ID
        @apiExample  {json} Example of JSON to upload
            {
              "informationelement": {
                  "@type": "Document",
                  "id": 728,
              },
              "weight": 0.9,
            }

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/validatedinformationelements", method = RequestMethod.POST)
    public ResponseEntity<InformationElementRelation>
        profilePostValidatedInformationElements(Authentication auth, @PathVariable Long id,
                                                @RequestBody InformationElementRelation validatedRelation)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        InformationElementRelation rel = updateProfile(id, validatedRelation, true, user);

        return new ResponseEntity<InformationElementRelation>(rel, HttpStatus.OK);
    }   

    /** @api {get} /profiles/:id/validatedinformationelements Get list of validated informationelements for profile
        @apiName GetValidatedInformationElements
        @apiParam {Number} id Profile's unique ID

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/validatedinformationelements", 
                    method = RequestMethod.GET)
    public ResponseEntity<InformationElementRelation[]>
        profileGetValidatedInformationElements(Authentication auth, @PathVariable Long id)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        List<InformationElementRelation> list = getProfile(id, user).validatedInformationElements;
        InformationElementRelation[] res = new InformationElementRelation[list.size()];
        list.toArray(res);

        return new ResponseEntity<InformationElementRelation[]>(res, HttpStatus.OK);
    }

    /** @api {delete} /profiles/:id/validatedinformationelements/:rid Delete validated informationelement from profile
        @apiName DeleteValidatedInformationElements
        @apiParam {Number} id Profile's unique ID
        @apiParam {Number} rid The ID of the validation relation
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}/validatedinformationelements/{rid}", 
                    method = RequestMethod.DELETE)
    public void profileDeleteValidatedInformationElements(Authentication auth, 
                                                          @PathVariable Long id, 
                                                          @PathVariable Long rid)
        throws NotFoundException
    {
        User user = getUser(auth);

        deleteProfileInformationElementRelation(id, rid, true, user);
    }   

    //--------------------------------------------------------------------------

    /** @api {post} /profiles/:id/tags Add a tag to the profile
        @apiName PostTags
        @apiParam {Number} id Profile's unique ID
        @apiExample  {json} Example of JSON to upload
            {
              "text": "mytag",
              "@type": "Tag"
            }

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/tags", method = RequestMethod.POST)
    public ResponseEntity<Tag>
        profilePostTag(Authentication auth, @PathVariable Long id, @RequestBody Tag tag)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);
        
        Profile profile = getProfile(id, user);
        profile.tags.add(tag);
        profile = storeProfile(profile, user);

        int n = profile.tags.size();
        return new ResponseEntity<Tag>(profile.tags.get(n-1), HttpStatus.OK);
    }   

    /** @api {get} /profiles/:id/tags Get list of tags for the profile
        @apiName GetTags
        @apiParam {Number} id Profile's unique ID

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @RequestMapping(value="/{id}/tags", method = RequestMethod.GET)
    public ResponseEntity<Tag[]> profileGetTags(Authentication auth, @PathVariable Long id)
        throws NotFoundException, BadRequestException
    {
        User user = getUser(auth);

        List<Tag> list = getProfile(id, user).tags;
        Tag[] res = new Tag[list.size()];
        list.toArray(res);

        return new ResponseEntity<Tag[]>(res, HttpStatus.OK);
    }

    /** @api {delete} /profiles/:id/tags/:tid Delete tags from profile
        @apiName DeleteTags
        @apiParam {Number} id Profile's unique ID
        @apiParam {Number} tid The ID of the tag
        @apiDescription On success, the response will be an empty HTTP 204.

        @apiPermission user
        @apiGroup Profiles
        @apiVersion 0.2.0
     */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}/tags/{tid}", method = RequestMethod.DELETE)
    public void profileDeleteTags(Authentication auth, @PathVariable Long id,
                                  @PathVariable Long tid)
        throws NotFoundException
    {
        User user = getUser(auth);

        Profile profile = getProfile(id, user);
        profile.removeTagById(tid);
        storeProfile(profile, user);
    }   
}
