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

import fi.hiit.dime.authentication.User;

import java.util.Collection;

/**
 * Higher-level interface to accessing users.
 */
public interface UserService {
    /**
     * Return user by user id.
     *
     * @param id User id
     * @return User with the given id
     */
    User getUserById(String id);

    /**
     * Return user by username.
     *
     * @param username The username
     * @return User with the given username
     */
    User getUserByUsername(String username);

    /**
     * Return a list of all users.
     */    
    Collection<User> getAllUsers();

    /**
     * Create a new user based on a filled in form.
     *
     * @param form The filled in form
     * @return The created user
     */
    User create(UserCreateForm form);

    /**
     * Remove user and all related events and informationelements
     * 
     * @param id User id of the user to be removed
     * @return True if a user was successfully removed
     */
    boolean removeAllForUserId(String id);
}
