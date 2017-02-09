/*
  Copyright (c) 2015-2016 University of Helsinki

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
import fi.hiit.dime.data.DiMeData;
import fi.hiit.dime.authentication.User;

import org.springframework.data.domain.Pageable;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

class InfoElemRepositoryImpl extends DiMeRepositoryImpl<InformationElement> {
    @Override
    public List<InformationElement> find(User user, Map<String, String> filterParams,
                                         int page, int limit, String order, boolean desc) {
        // We build the SQL query into q
        StringBuilder q = new StringBuilder("select e from InformationElement e "
                                            + "where e.user.id=:userId");

        // Map for storing named parameters for the query we are
        // constructing
        Map<String, Object> namedParams = new HashMap<String, Object>();

        // Loop over user's parameters, and transform to SQL statments
        // and fill in namedParams
        for (Map.Entry<String, String> param : filterParams.entrySet()) {
            String name = param.getKey().toLowerCase();
            String value = param.getValue();

            String criteria = "";

            switch (name) {
            case "tag":
                criteria = "(select count(*) from e.tags where text=:tag) > 0";
                break;
            case "appid":
                name = "appId";
                break;
            case "contenthash":
                name = "contentHash";
                break;
            case "plaintextcontent":
                name = "plainTextContent";
                break;
            case "isstoredas":
                name = "isStoredAs";
                break;
            case "mimetype":
                name = "mimeType";
                break;
            case "@type":
                criteria = "e.class=:myclass";
                namedParams.put("myclass", value);
                value = null;
                break;
            case "uri":
            case "type":
            case "title":
                break;
            default:
                throw new IllegalArgumentException(name);
            }

            if (criteria.isEmpty())
                criteria = String.format("%s=:%s", name, name);

            q.append(" and " + criteria);
            if (value != null)
                namedParams.put(name, value);
        }

        if (order != null) {
            switch (order) {
            case "timeModified":
            case "timeCreated":
                q.append(" order by " + order);
                if (desc)
                    q.append(" desc");
                else
                    q.append(" asc");
                break;
            default:
                throw new IllegalArgumentException(order);
            }
        }            

        return makeQuery(q.toString(), namedParams, page, limit, user,
                         InformationElement.class).getResultList();
    }
}

public interface InfoElemRepository extends DiMeRepository<InformationElement> {
    List<InformationElement> 
        findByUserOrderByTimeModifiedDesc(User user, Pageable pageable);
}
