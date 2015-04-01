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

import fi.hiit.dime.authentication.UserCreateForm;
import fi.hiit.dime.authentication.UserCreateFormValidator;
import fi.hiit.dime.authentication.UserService;
import javax.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.validation.BindingResult;
import org.springframework.validation.ObjectError;
import org.springframework.web.bind.WebDataBinder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurerAdapter;

//------------------------------------------------------------------------------

@Controller
public class UserController extends WebMvcConfigurerAdapter {
    private static final Logger LOGGER = LoggerFactory.getLogger(UserController.class);

    private final UserService userService;
    private final UserCreateFormValidator userCreateFormValidator;

    @Autowired
    UserController(UserService userService,
		   UserCreateFormValidator userCreateFormValidator) {
	this.userService = userService;
	this.userCreateFormValidator = userCreateFormValidator;
    }

    @InitBinder("from")
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
    public String handleUserCreateForm(@Valid @ModelAttribute("form") UserCreateForm form,
				       BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
	    LOGGER.debug("has errors");
            return "user_create";
        }
        try {
            userService.create(form);
        } catch (DataIntegrityViolationException e) {
            bindingResult.reject("username.exists", "Username already exists");
            return "user_create";
        }
        return "redirect:/users";
    }    

    /** Viewing users, FIXME: should be accessible only to ADMIN users */
    @RequestMapping("/users")
    public ModelAndView getUsersPage() {
        return new ModelAndView("users", "users", userService.getAllUsers());
    }

    // @RequestMapping("/user/{id}")
    // public ModelAndView getUserPage(@PathVariable Long id) {
    //     return new ModelAndView("user", "user", userService.getUserById(id)
    //             .orElseThrow(() -> new NoSuchElementException(String.format("User=%s not found", id))));
    // }

}
