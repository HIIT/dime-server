package fi.hiit.dime.database;

import java.util.List;
import org.springframework.data.mongodb.repository.MongoRepository;

import fi.hiit.dime.data.ZgSubject;

public interface ZgSubjectRepository extends MongoRepository<ZgSubject, String> {
}
