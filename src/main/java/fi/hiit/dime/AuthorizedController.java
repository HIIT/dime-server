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

package fi.hiit.dime;

import fi.hiit.dime.authentication.CurrentUser;
import fi.hiit.dime.authentication.User;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.http.HttpStatus;

import javax.servlet.http.HttpServletRequest;

/**
 * Base class for controllers that need user authentication.
 *
 * @author Mats Sjöberg, mats.sjoberg@helsinki.fi
 */
public class AuthorizedController {
    protected User getUser(Authentication auth) {
        if (auth == null)
            return null;

        CurrentUser currentUser = (CurrentUser)auth.getPrincipal();
        return currentUser.getUser();
    }

    @ResponseStatus(value=HttpStatus.UNAUTHORIZED)
    public class NotAuthorizedException extends Exception {
        public NotAuthorizedException(String msg) {
            super(msg);
        }
    }

    @ResponseStatus(value=HttpStatus.BAD_REQUEST)
    public class BadRequestException extends Exception {
        public BadRequestException(String msg) {
            super(msg);
        }
    }

    @ResponseStatus(value=HttpStatus.NOT_FOUND)
    public class NotFoundException extends Exception {
        public NotFoundException(String msg) {
            super(msg);
        }
    }

    public boolean isLocalhost(HttpServletRequest req) {
        String addr = req.getRemoteAddr();
        return addr.equals("0:0:0:0:0:0:0:1") || 
            addr.equals("127.0.0.1") || 
            addr.startsWith("172.17."); // Docker
    }
}
