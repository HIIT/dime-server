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

import fi.hiit.dime.database.*;
import fi.hiit.dime.util.RandomPassword;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Sort;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.util.Collection;
import javax.annotation.PostConstruct;

/**
   Service that gives us a general interface to fetch and create users
   independent of the underlying user database.
*/
@Service
public class UserServiceImpl implements UserService {
    private static final Logger LOG = LoggerFactory.getLogger(UserServiceImpl.class);
    private final UserDAO userDAO;
    private final EventDAO eventDAO;
    private final InformationElementDAO infoElemDAO;
    private final ProfileDAO profileDAO;
    private final static String ADMIN_USERNAME = "admin";
    private final static String ADMIN_PASSWORD = ""; // empty means random
    private RandomPassword pw;

    @Autowired
    UserServiceImpl(UserDAO userDAO, EventDAO eventDAO,
		    InformationElementDAO infoElemDAO,
                    ProfileDAO profileDAO) {
	this.userDAO = userDAO;
	this.eventDAO = eventDAO;
	this.infoElemDAO = infoElemDAO;
        this.profileDAO = profileDAO;
	this.pw = new RandomPassword();
    }

    /** 
	This method is run on startup, to create a default admin user
	if it is not already present.
    */
    @PostConstruct
    public void installAdminUser() {
	if (getUserByUsername(ADMIN_USERNAME) == null) {
	    String passwd = ADMIN_PASSWORD;
	    if (passwd.isEmpty())
		passwd = pw.getPassword(20, true, false);

	    UserCreateForm form = new UserCreateForm();
	    form.setUsername(ADMIN_USERNAME);
	    form.setPassword(passwd);
	    form.setRole(Role.ADMIN);

	    create(form);

	    System.out.printf("\nCreated default admin user with password " +
			      "\"%s\"\n\n.", passwd);
	}
    }

    @Override
    public User getUserById(Long id) {
	return userDAO.findById(id);
    }

    @Override
    public User getUserByUsername(String username) {
    	return userDAO.findByUsername(username);
    }
    
    @Override
    public Collection<User> getAllUsers() {
	return userDAO.findAll();
    }

    @Override
    public User create(UserCreateForm form) {
	User user = new User();
	user.username = form.getUsername();
	user.passwordHash = new BCryptPasswordEncoder().encode(form.getPassword());
	user.role = form.getRole();
	userDAO.save(user);
	return user;
    }
    
    @Override
    public boolean removeAllForUserId(Long id) {
        profileDAO.removeForUser(id);
	eventDAO.removeForUser(id);
	infoElemDAO.removeForUser(id);
	userDAO.remove(id);
	return true;
    }

}
