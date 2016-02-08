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

import java.util.Map;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;


import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.NoRepositoryBean;

import java.util.List;

interface DiMeRepositoryCustom<T extends DiMeData> {
    public List<T> find(User user, Map<String, String> filterParams);
    public T replace(T oldData, T newData);
}

abstract class DiMeRepositoryImpl<T extends DiMeData> implements DiMeRepositoryCustom<T> {
    @PersistenceContext
    protected EntityManager entityManager;

    // Java Persistence Query Language Syntax:
    // http://docs.oracle.com/javaee/6/tutorial/doc/bnbuf.html
    TypedQuery<T> makeQuery(String q, Map<String, String> params,
				User user, Class<T> resultClass) 
    {
        TypedQuery<T> query = entityManager.createQuery(q, resultClass);
	System.out.println("Find query: " + q);

	query = query.setParameter("userId", user.getId());
	System.out.println("  param: userId = " + user.getId());

	for (Map.Entry<String, String> p : params.entrySet()) {
	    System.out.println("  param: " + p.getKey() + " = " + p.getValue());
	    query = query.setParameter(p.getKey(), p.getValue());
	}

	return query;
    }

    @Override
    public T replace(T oldData, T newData) {
        newData.copyIdFrom(oldData);
        return entityManager.merge(newData);
    }
}

@NoRepositoryBean
public interface DiMeRepository<T extends DiMeData>
    extends CrudRepository<T, Long>, DiMeRepositoryCustom<T> 
{
    T findOne(Long id);

    T findOneByIdAndUser(Long id, User user);

    T findOneByAppIdAndUser(String appId, User user);

    List<T> findByUser(User user);

    Long countByUser(User user);

    Long deleteByUser(User user);
}
