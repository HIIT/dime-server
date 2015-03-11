package fi.hiit.dime.data;

import org.springframework.data.annotation.Id;
import java.util.Date;

/**
   Base class for all DiMe data objects, i.e. data items uploaded to be stored.
*/
public class DiMeData {

    /** Unique identifier in the database */
    @Id
    public String id;

    /** Date and time when the object was first uploaded via the
	external API. 
     */
    public Date time_created;

    /** Date and time when the objects was last modified via the
	external API.
    */
    public Date time_modified;

    /** Type of data object.
	FIXME defined DiMe ontology for interpretation.
     */
    public String interpretation;

    /** How the data object was created.
	FIXME defined DiMe ontology for manifestation.
     */
    public String manifestation;


    public DiMeData() {
	// Set to current date and time
	time_created = new Date();
	time_modified = new Date();
    }	
}
