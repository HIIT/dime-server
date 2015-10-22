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
import fi.hiit.dime.authentication.UserCreateForm;
import fi.hiit.dime.authentication.UserCreateFormValidator;
import fi.hiit.dime.authentication.UserService;
import fi.hiit.dime.data.*;
import fi.hiit.dime.database.*;

import org.slf4j.Logger;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

import java.io.IOException;
import java.net.InetAddress;
import java.util.List;
import java.util.NoSuchElementException;
import javax.validation.Valid;
import java.net.UnknownHostException;

/**
 * Web UI controller.
 *
 * @author Mats Sjöberg, mats.sjoberg@helsinki.fi
 */
@Controller
public class WebController extends WebMvcConfigurerAdapter {
    private static final Logger LOG = 
	LoggerFactory.getLogger(WebController.class);

    @Autowired
    private DiMeProperties dimeConfig;

    @Autowired
    private EventDAO eventDAO;

    @Autowired
    private InformationElementDAO infoElemDAO;

    @Autowired
    private UserService userService;

    @Autowired
    private UserCreateFormValidator userCreateFormValidator;

    @Autowired
    SearchIndex searchIndex;


    //------------------------------------------------------------------------------
    // Various "regular" pages
    //------------------------------------------------------------------------------

    @RequestMapping("/")
    public String root(Model model, @RequestHeader("host") String hostName) {	
	try {
	    hostName = InetAddress.getLocalHost().getHostName();
	} catch (UnknownHostException e) {
	}

	model.addAttribute("hostname", hostName);
        return "root";
    }

    /* Show log of all data */
    @RequestMapping("/log")
    public String log(Authentication authentication, Model model) {
	String userId = ((CurrentUser)authentication.getPrincipal()).getId();
        model.addAttribute("events", eventDAO.eventsForUser(userId));
	model.addAttribute("count", eventDAO.count(userId));
        return "log";
    }

    /* Show a specific event */
    @RequestMapping("/event")
    public String event(Authentication authentication, Model model,
		      @RequestParam(value="id") String eventId) {
	String userId = ((CurrentUser)authentication.getPrincipal()).getId();
	Event event = eventDAO.findById(eventId);

	if (event.user.getId().equals(userId))
	    model.addAttribute("event", event);
        return "event";
    }

    /* Show a specific information element */
    @RequestMapping("/infoelem")
    public String infoElem(Authentication authentication, Model model,
			   @RequestParam(value="id") String elemId) {
	String userId = ((CurrentUser)authentication.getPrincipal()).getId();
	InformationElement elem = infoElemDAO.findById(elemId);

	if (elem.user.getId().equals(userId)) {
	    model.addAttribute("elem", elem);
	    model.addAttribute("long", true);
	}

        return "infoelem";
    }

    /* Show a specific message object */
    @RequestMapping("/message")
    public String message(Authentication authentication, Model model,
			  @RequestParam(value="id") String elemId) {
	String userId = ((CurrentUser)authentication.getPrincipal()).getId();
	Message elem = (Message)infoElemDAO.findById(elemId);

	if (elem.user.getId().equals(userId))
	    model.addAttribute("elem", elem);
        return "message";
    }

    /* Search page */
    @RequestMapping("/search")
    public String search(@ModelAttribute SearchQuery search,
			 Authentication authentication,
			 Model model) {

	String userId = ((CurrentUser)authentication.getPrincipal()).getId();
	model.addAttribute("info", "");

	String query = search.getQuery();
	if (!query.isEmpty()) {
	    List<InformationElement> results = null;
	    if (dimeConfig.getUseLucene()) {
		try {
		    results = searchIndex.textSearch(query, 100, userId);
		    model.addAttribute("info", "(Lucene)");
		} catch (IOException e) {
		    LOG.warn("Lucene search failed [" + e + "].");
		    model.addAttribute("error", e);
		}
	    }

	    model.addAttribute("results", results);
	}

        model.addAttribute("search", search);


        return "search";
    }


    //------------------------------------------------------------------------------
    // User management
    //------------------------------------------------------------------------------

    @RequestMapping(value = "/login", method = RequestMethod.GET)
    public ModelAndView getLoginPage(@RequestParam(required=false) String error) {
        return new ModelAndView("login", "error", error);
    }

    @InitBinder("form")
    public void initBinder(WebDataBinder binder) {
        binder.addValidators(userCreateFormValidator);
    }

    /* Web page for registering a new user */
    @RequestMapping(value = "/user/create", method = RequestMethod.GET)
    public ModelAndView getUserCreatePage() {
        return new ModelAndView("user_create", "form", new UserCreateForm());
    }

    /* Handles processing of the new user registration form */
    @RequestMapping(value = "/user/create", method = RequestMethod.POST)
    public String handleUserCreateForm(@Valid @ModelAttribute("form") 
				       UserCreateForm form,
				       BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return "user_create";
        }
        try {
	    // FIXME: check that only admin can create other admin user
            userService.create(form);
        } catch (DataIntegrityViolationException e) {
            bindingResult.rejectValue("username", "exists",
				      "This user name is no longer available.");
            return "user_create";
        }
        return "redirect:/";
    }    

    /* Viewing users */
    @RequestMapping("/users")
    public ModelAndView getUsersPage() {
        return new ModelAndView("users", "users", userService.getAllUsers());
    }

    @PreAuthorize("@currentUserServiceImpl.canAccessUser(principal, #name)")
    @RequestMapping("/user/{name}")
    public ModelAndView getUserPage(@PathVariable("name") String name) {
	User user = userService.getUserByUsername(name);
	if (user == null)
	    throw new NoSuchElementException(String.format("User %s not found",
							   name));
        return new ModelAndView("user", "user", user);
    }
}
