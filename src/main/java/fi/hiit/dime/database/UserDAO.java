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

package fi.hiit.dime.database;

//------------------------------------------------------------------------------

import fi.hiit.dime.data.User;
import java.util.List;
import org.springframework.stereotype.Repository;
import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;

//------------------------------------------------------------------------------

@Repository
public class UserDAO extends BaseDAO<User> {

    //--------------------------------------------------------------------------

    @Override
    public String collectionName() { 
	return "user";
    }

    //--------------------------------------------------------------------------

    public User findById(String id) {
    	return operations.findById(id, User.class, collectionName());
    }


    //--------------------------------------------------------------------------

    public User findByUsername(String username) {
    	return operations.findOne(query(where("username").is(username)), User.class, collectionName());
    }

    //------------------------------------------------------------------------------

    public List<User> findAll() {
    	return operations.findAll(User.class, collectionName());
    }

}
