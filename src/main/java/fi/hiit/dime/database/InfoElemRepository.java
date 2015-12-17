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

import fi.hiit.dime.data.InformationElement;
import fi.hiit.dime.authentication.User;

import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.CrudRepository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

interface InfoElemRepositoryCustom {
    public List<InformationElement> find(User user, Map<String, String> filterParams);
    public InformationElement replace(InformationElement oldElem, 
				      InformationElement newElem);
}

class InfoElemRepositoryImpl extends BaseRepository implements InfoElemRepositoryCustom {
    public List<InformationElement> find(User user, Map<String, String> filterParams) {
	// We build the SQL query into q
	StringBuilder q = new StringBuilder("select e from InformationElement e " +
					    "where user.id=:userId");

	// Map for storing named parameters for the query we are
	// constructing
	Map<String, String> namedParams = new HashMap<String, String>();

	// Loop over user's parameters, and transform to SQL statments
	// and fill in namedParams
	for (Map.Entry<String, String> param : filterParams.entrySet()) {
    	    String name = param.getKey().toLowerCase();
    	    String value = param.getValue();

	    String criteria = "";

    	    switch (name) {
    	    case "tag":
		criteria = ":tag member of e.tags";
    		break;
            case "appid":
            name = "appId";
            criteria = String.format("%s=:%s", name, name);
            break;
            case "contenthash":
            name = "contentHash";
            criteria = String.format("%s=:%s", name, name);
            break;
            case "plaintextcontent":
            name = "plainTextContent";
            criteria = String.format("%s=:%s", name, name);
            break;
            case "isstoredas":
            name = "isStoredAs";
            criteria = String.format("%s=:%s", name, name);
            break;
            case "mimetype":
            name = "mimeType";
            criteria = String.format("%s=:%s", name, name);
            break;
            case "uri":
    	    case "type":
    	    case "title":
            criteria = String.format("%s=:%s", name, name);
    		break;
    	    default:
    		throw new IllegalArgumentException(name);
    	    }

	    q.append(" and " + criteria);
	    namedParams.put(name, value);
    	}

	return makeQuery(q.toString(), namedParams, user,
			 InformationElement.class).getResultList();
    }

    public InformationElement replace(InformationElement oldElem,
				      InformationElement newElem) 
    {
	newElem.copyIdFrom(oldElem);
	return entityManager.merge(newElem);
    }
}

public interface InfoElemRepository extends CrudRepository<InformationElement, Long>,
					    InfoElemRepositoryCustom {
    InformationElement findOne(Long id);

    InformationElement findOneByIdAndUser(Long id, User user);

    InformationElement findOneByAppIdAndUser(String appId, User user);

    List<InformationElement> findByUser(User user);

    List<InformationElement> 
    	findByUserOrderByTimeModifiedDesc(User user, Pageable pageable);

    Long countByUser(User user);

    Long deleteByUser(User user);
}
