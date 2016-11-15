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

import fi.hiit.dime.authentication.Role;
import fi.hiit.dime.authentication.User;
import fi.hiit.dime.authentication.UserService;
import fi.hiit.dime.authentication.UserService.CannotCreateUserException;
import fi.hiit.dime.database.UserDAO;

import com.fasterxml.jackson.annotation.JsonInclude;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
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
import java.util.Collection;

import javax.servlet.http.HttpServletRequest;

/**
 * General API controller, for things that go directly under the /api
 * REST endpoint.
 *
 * @author Mats Sjöberg, mats.sjoberg@helsinki.fi
 */
@RestController
@RequestMapping("/api/users")
public class UsersController extends AuthorizedController {
    private static final Logger LOG =
        LoggerFactory.getLogger(UsersController.class);

    // private final UserDAO userDAO;
    // @Autowired
    private final UserService userService;

    @Autowired
    UsersController(UserService userService) {
        this.userService = userService;
    }


    /** HTTP end point for creating a new user, i.e., registering. 
        @api {post} /users Create a new user
        @apiName Post
        @apiDescription Create a new user.  Must be authenticated as an existing user, or accessing from localhost.
        
        @apiExample {json} Example of JSON to upload
            {
              "@type": "User",
              username: "testuser",
              password: "testuser123",
              email: "testuser@example.com"
            }

        @apiGroup Users
        @apiVersion 0.1.3
    */
    @RequestMapping(value="", method = RequestMethod.POST)
    public ResponseEntity<User> postUsers(Authentication auth, 
                                          @RequestBody User input,
                                          HttpServletRequest req)
        throws BadRequestException, NotAuthorizedException
    {
        User authUser = getUser(auth);

        if (authUser == null && !isLocalhost(req))
            throw new NotAuthorizedException("Access denied.");
        
        // More secure to explicitly copy just fields we want
        User newUser = new User();
        newUser.username = input.username;
        newUser.email = input.email;

        newUser.role = Role.USER;

        try {
            User createdUser = userService.create(newUser, input.password);
            return new ResponseEntity<User>(createdUser, HttpStatus.OK);
        } catch (CannotCreateUserException ex) {
            throw new BadRequestException(ex.getMessage());
        }
    }   

    /** HTTP end point for accessing a given user. 
        @api {get} /users/:id Access user
        @apiName Get
        @apiParam {Number} id User's unique ID
        @apiDescription Access a given user. Non-admin users can only access themselves.

        @apiPermission user
        @apiGroup Users
        @apiVersion 0.1.3
     */
    @RequestMapping(value="/{id}", method = RequestMethod.GET)
    public ResponseEntity<User> getusers(Authentication auth, @PathVariable Long id) 
        throws NotFoundException
    {
        User authUser = getUser(auth);
        User user = userService.getUserById(id);

        boolean canAccess = (user != null) && 
            (authUser.role == Role.ADMIN ||
             (authUser.role == Role.USER && authUser.getId().equals(user.getId())));

        // We claim "not found" in all cases as not to leak information.
        if (!canAccess)
            throw new NotFoundException("User not found");

        return new ResponseEntity<User>(user, HttpStatus.OK);
    }   

    /** HTTP end point for accessing all users.

        @api {get} /users Access all users
        @apiName GetAll
        @apiDescription Access all users.  For non-admin users this returns only the logged in user.

        @apiPermission user
        @apiGroup Users
        @apiVersion 0.1.3
    */    
    @RequestMapping(value="", method = RequestMethod.GET)
    public ResponseEntity<User[]> getAllUsers(Authentication auth) 
        throws BadRequestException
    {
        User authUser = getUser(auth);
        
        Collection<User> users = new ArrayList<User>();

        if (authUser.role == Role.ADMIN)
            users = userService.getAllUsers();
        else if (authUser.role == Role.USER)
            users.add(userService.getUserById(authUser.getId()));

        User[] usersArray = new User[users.size()];
        users.toArray(usersArray);

        return new ResponseEntity<User[]>(usersArray, HttpStatus.OK);
    }


    /** HTTP end point for deleting a user.         
        
        @api {delete} /users/:id Delete user
        @apiName Delete
        @apiParam {Number} id User's unique ID
        @apiDescription On success, the response will be an empty HTTP 204.  Non-admin users can only delete themselves.

        @apiPermission user
        @apiGroup Users
        @apiVersion 0.1.3
    */
    @ResponseStatus(value = HttpStatus.NO_CONTENT)
    @RequestMapping(value="/{id}", method = RequestMethod.DELETE)
    public void userDelete(Authentication auth, @PathVariable Long id) 
        throws NotFoundException
    {
        User authUser = getUser(auth);
        User user = userService.getUserById(id);

        boolean canAccess = (user != null) && 
            (authUser.role == Role.ADMIN ||
             (authUser.role == Role.USER && authUser.getId().equals(user.getId())));

        // We claim "not found" in all cases as not to leak information.
        if (!canAccess)
            throw new NotFoundException("User not found");

        if (!userService.removeAllForUserId(id))
            throw new NotFoundException("User not found");
    }
}
