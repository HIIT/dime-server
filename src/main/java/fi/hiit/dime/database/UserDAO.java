/*
  Copyright (c) 2015-2017 University of Helsinki

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

package fi.hiit.dime.database;


import fi.hiit.dime.authentication.User;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

/**
 * Data access object for managing User objects.
 *
 * @author Mats Sjöberg (mats.sjoberg@helsinki.fi)
 */
@Repository
public class UserDAO {

    @Autowired
    private UserRepository repo;

    public User save(User obj) {
        return repo.save(obj);
    }

    private void ensureUserId(User user) {
        if (user != null && user.userId == null) {
            user.userId = UUID.randomUUID().toString();
            save(user);
        }
    }

    public User findById(Long id) {
        User user = repo.findOne(id);
        ensureUserId(user);
        return user;
    }

    public User findByUsername(String username) {
        User user = repo.findOneByUsername(username);
        ensureUserId(user);
        return user;
    }

    public List<User> findAll() {
        List<User> users = repo.findAll();
        for (User user : users)
            ensureUserId(user);
        return users;
    }

    public void remove(Long id) {
        repo.delete(id);
    }
}
