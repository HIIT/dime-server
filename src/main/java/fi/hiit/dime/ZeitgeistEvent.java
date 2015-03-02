package fi.hiit.dime;

import org.springframework.data.annotation.Id;
import java.util.Date;

public class ZeitgeistEvent {
    @Id
    private String id;
    
    // private String zid;
    private String actor;

    private String manifestation;
    private String interpretation;

    private String origin;
    private Date timestamp;
    
    private String subject_uri;
    private String subject_manifestation;
    private String subject_interpretation;
    private String subject_mimetype;

    private String payload;

    public ZeitgeistEvent() {}

    public ZeitgeistEvent(String actor, 
			  String manifestation, 
			  String interpretation,
			  String origin,
			  Date timestamp,
			  String subject_uri,
			  String subject_manifestation,
			  String subject_interpretation,
			  String subject_mimetype,
			  String payload) {
    	this.actor = actor;
    	this.manifestation = manifestation;
	this.interpretation = interpretation;
	this.origin = origin;
    	this.timestamp = timestamp;
	this.subject_uri = subject_uri;
	this.subject_manifestation = subject_manifestation;
	this.subject_interpretation = subject_interpretation;
	this.subject_mimetype = subject_mimetype;
	this.payload  = payload;
    }

    public String getActor() { return actor; }
    public String getManifestation() { return manifestation; }
    public String getInterpretation() { return interpretation; }
    public String getOrigin() { return origin; }
    public Date getTimestamp() { return timestamp; }
    public String getSubject_uri() { return subject_uri; }
    public String getSubject_manifestation() { return subject_manifestation; }
    public String getSubject_interpretation() { return subject_interpretation; }
    public String getSubject_mimetype() { return subject_mimetype; }
    public String getPayload() { return payload; }
}
