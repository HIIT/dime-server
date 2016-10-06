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

import fi.hiit.dime.data.DiMeData;
import fi.hiit.dime.authentication.User;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class DiMeDAO<T extends DiMeData, R extends DiMeRepository<T>> {
    @Autowired
    protected R repo;

    @Transactional
    public void save(T obj) {
        if (obj.timeCreated == null)
            obj.timeCreated = new Date();
        obj.timeModified = new Date();

        notIndexed.add(obj);
        repo.save(obj);
    }

    @Transactional
    public T replace(T oldObj, T newObj) {
        newObj.timeModified = new Date();
        return repo.replace(oldObj, newObj);
    }

    /**
       Find a single DiMeData object by its unique id.

       @param id Unique id of DiMeData object.
       @return The DiMeData object found.
    */
    @Transactional(readOnly = true)
    public T findById(Long id) {
        return repo.findOne(id);
    }

    /**
       Find a single DiMeData object by its unique id, and user.

       @param id Unique id of DiMeData object.
       @param user User
       @return The DiMeData object found.
    */
    @Transactional(readOnly = true)
    public T findById(Long id, User user) {
        return repo.findOneByIdAndUser(id, user);
    }

    /**
       Find a single DiMeData object by its appId.

       @param appId Appliction id
       @param user User
       @return The DiMeData object found.
    */
    @Transactional(readOnly = true)
    public T findByAppId(String appId, User user) {
        List<T> items = repo.findByAppIdAndUserOrderByTimeModifiedDesc(appId,
                                                                       user);
        if (items.size() > 0)
            return items.get(0);
        
        return null;
    }

    /**
       Returns all DiMeData objects.
    */
    @Transactional(readOnly = true)
    public Iterable<T> findAll() {
        return repo.findAll();
    }

    /**
       Filtered search for a given user's data.

       @param userId User id
       @param filterParams Filtering parameters
       @return List of matching DiMeData objects
    */
    @Transactional(readOnly = true)
        public List<T> find(Long userId, Map<String, String> filterParams, 
                            int page, int limit) {
        return repo.find(User.makeUser(userId), filterParams, page, limit);
    }

    @Transactional(readOnly = true)
    public long count(Long id) {
        return repo.countByUser(User.makeUser(id));
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
       Removes a single item.

       @param id Item id
       @param user User
       @return True if it was deleted, false otherwise.
    */
    @Transactional
    public boolean remove(Long id, User user) {
        T d = findById(id, user);
        if (d == null || !d.user.getId().equals(user.getId()))
            return false;

        repo.delete(d);
        return true;
    }

    @Transactional(readOnly = true) 
    public List<T> checkedList(List<T> origList, User user) {
        if (origList == null)
            return null;

        List<T> ret = new ArrayList<T>();

        for (T d : origList) {
            T checkedData = findById(d.getId(), user);
            if (checkedData != null)
                ret.add(checkedData);
        }

        return ret;
    }

    protected Set<T> notIndexed = new HashSet<T>();

    public int countNotIndexed() {
        return notIndexed.size();
    }

    public boolean hasUnIndexed() {
        return !notIndexed.isEmpty();
    }

    public Set<T> getNotIndexed() {
        Set<T> ret = new HashSet<T>();

        // Return only items that still exist
        for (T d : notIndexed) {
            T toAdd = findById(d.getId());
            if (toAdd != null)
                ret.add(toAdd);
        }

        return ret;
    }

    public void clearNotIndexed() {
        notIndexed.clear();
    }
}
