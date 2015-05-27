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

package fi.hiit.dime.data;

//------------------------------------------------------------------------------

import org.springframework.data.annotation.Id;
import java.util.Date;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;

//------------------------------------------------------------------------------

/**
   Class for storing users and associated information for this DiMe.
*/
@JsonInclude(value=JsonInclude.Include.NON_NULL)
public class User {

    /** Unique identifier in the database */
    @Id
    public String id;
    
    /** Unique username */
    public String username;
    
    /** Hash of password (never store the actual password!) */
    @JsonIgnore public String passwordHash;
    
    /** Email */
    public String email;       
    
    /** Date and time when the user was registered */
    public Date time_registered;
    
    /** Date and time when the user last logged in */ 
    public Date time_login;
    
    /** User role, e.g. user or admin. */
    public Role role;
}
