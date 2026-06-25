package com.example.join;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class EnrollmentMapper extends Mapper<LongWritable, Text, Text, Text> {

    private static final String ENROLL_TAG = "enroll~";
    private static final String DATA_SEPARATOR = ",";

    @Override
    public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();

        // Skip header row
        if (line.startsWith("Enrollment_ID")) {
            return;
        }

        String[] parts = line.split(DATA_SEPARATOR);

        // Expected format: Enrollment_ID, Course_ID, Student_Name, EnrollmentDate, ...
        // We need at least 4 parts for Enrollment_ID, Course_ID, Student_Name, EnrollmentDate
        if (parts.length >= 4) {
            String courseId = parts[1].trim();
            String studentName = parts[2].trim();
            String enrollmentDate = parts[3].trim();

            // Emit (Course_ID, 'enroll~'+ Student_Name +','+ EnrollmentDate)
            context.write(new Text(courseId), new Text(ENROLL_TAG + studentName + DATA_SEPARATOR + enrollmentDate));
        } else {
            // Handle malformed lines or log errors if necessary
            context.getCounter("EnrollmentMapper", "Malformed Records").increment(1);
        }
    }
}
