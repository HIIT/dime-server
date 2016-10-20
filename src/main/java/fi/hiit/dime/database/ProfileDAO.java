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

package fi.hiit.dime.database;

import fi.hiit.dime.authentication.User;
import fi.hiit.dime.data.Profile;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;

@Service
public class ProfileDAO {
    @Autowired
    protected ProfileRepository repo;

    @Transactional
    public void save(Profile obj) {
        if (obj.timeCreated == null)
            obj.timeCreated = new Date();
        obj.timeModified = new Date();

        repo.save(obj);
    }

    // @Transactional
    // public Profile replace(Profile oldObj, Profile newObj) {
    //     newObj.timeModified = new Date();
    //     return repo.replace(oldObj, newObj);
    // }

    /**
       Find a single Profile by its unique id.

       @param id Unique id of the Profile.
       @return The Profile found.
    */
    @Transactional(readOnly = true)
    public Profile findById(Long id) {
        return repo.findOne(id);
    }

    /**
       Find a single Profile by its unique id, and user.

       @param id Unique id of Profile.
       @param user User
       @return The Profile found.
    */
    @Transactional(readOnly = true)
    public Profile findById(Long id, User user) {
        return repo.findOneByIdAndUser(id, user);
    }

    /**
       Profiles for user.

       @param userId User id
    */
    @Transactional(readOnly = true)
    public List<Profile> profilesForUser(Long userId) {
        return repo.findByUser(User.makeUser(userId));
    }

    /**
       Removes all items for user.

       @param id User id
       @return Number of items removed.
    */
    @Transactional
    public long removeForUser(Long id) {
        return repo.deleteByUser(User.makeUser(id));
    }

    /**
       Removes a single profile item.

       @param id Profile id
       @param user User
       @return True if it was deleted, false otherwise.
    */
    @Transactional
    public boolean remove(Long id, User user) {
        Profile p = findById(id, user);
        if (p == null || !p.user.getId().equals(user.getId()))
            return false;

        repo.delete(p);
        return true;
    }
    
}
