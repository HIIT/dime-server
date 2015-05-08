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

package fi.hiit.dime.authentication;

//------------------------------------------------------------------------------

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

//------------------------------------------------------------------------------

@Component
public class UserCreateFormValidator implements Validator {
    private static final Logger LOG = LoggerFactory.getLogger(UserCreateFormValidator.class);
    private static final int MIN_PASSWORD_LENGTH = 3;

    private final UserService userService;

    @Autowired
    public UserCreateFormValidator(UserService userService) {
        this.userService = userService;
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return clazz.equals(UserCreateForm.class);
    }

    @Override
    public void validate(Object target, Errors errors) {
        UserCreateForm form = (UserCreateForm)target;
        validatePasswords(errors, form);
        validateUsername(errors, form);
    }

    private void validatePasswords(Errors errors, UserCreateForm form) {
        if (!form.getPassword().equals(form.getPasswordRepeated()))
            errors.rejectValue("passwordRepeated", "match",
			       "Passwords do not match.");

        if (form.getPassword().length() < MIN_PASSWORD_LENGTH)
            errors.rejectValue("password", "short",
			       String.format("Password is too short! "+
					     "Please use at least %d characters.",
					     MIN_PASSWORD_LENGTH));
    }

    private void validateUsername(Errors errors, UserCreateForm form) {
        if (userService.getUserByUsername(form.getUsername()) != null)
            errors.rejectValue("username", "exists",
			       "This user name is no longer available.");
    }
}
