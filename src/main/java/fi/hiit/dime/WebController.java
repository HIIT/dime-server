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
import fi.hiit.dime.authentication.UserCreateForm;
import fi.hiit.dime.authentication.UserCreateFormValidator;
import fi.hiit.dime.authentication.UserService;
import fi.hiit.dime.data.User;
import fi.hiit.dime.database.ZgEventRepository;
import java.util.NoSuchElementException;
import javax.validation.Valid;
import org.slf4j.Logger;
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

//------------------------------------------------------------------------------

@Controller
public class WebController extends WebMvcConfigurerAdapter {
    private static final Logger LOG = 
	LoggerFactory.getLogger(WebController.class);

    @Autowired
    private ZgEventRepository zgEventRepository;

    //@Autowired
    //private Authentication authentication;

    @Autowired
    private UserService userService;

    @Autowired
    private UserCreateFormValidator userCreateFormValidator;


    // private CurrentUser getCurrentUser() {
    // 	// return (CurrentUser)authentication.getPrincipal();
    // 	return new CurrentUser();
    // }

    @RequestMapping("/")
    public String root(Model model) {
        return "root";
    }

    @RequestMapping("/log")
    public String log(Authentication authentication, Model model) {
	String userId = ((CurrentUser)authentication.getPrincipal()).getId();
        model.addAttribute("events", 
			   zgEventRepository.eventsForUser(userId));
        return "log";
    }

    @RequestMapping(value = "/login", method = RequestMethod.GET)
    public ModelAndView getLoginPage(@RequestParam(required=false) String error) {
        return new ModelAndView("login", "error", error);
    }

    @InitBinder("form")
    public void initBinder(WebDataBinder binder) {
        binder.addValidators(userCreateFormValidator);
    }

    /** Web page for registering a new user */
    @RequestMapping(value = "/user/create", method = RequestMethod.GET)
    public ModelAndView getUserCreatePage() {
        return new ModelAndView("user_create", "form", new UserCreateForm());
    }

    /** Handles processing of the new user registration form */
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

    /** Viewing users */
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
