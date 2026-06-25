package com.example.join;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.MultipleInputs;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
import org.apache.log4j.Logger;

public class EnrollmentJoinDriver extends Configured implements Tool {

    private static final String DATA_SEPARATOR = ",";
    private static Logger logger = Logger.getLogger(EnrollmentJoinDriver.class);

    @Override
    public int run(String[] args) throws Exception {
        if (args.length != 3) {
            logger.error("Usage: EnrollmentJoinDriver <course_input_path> <enrollment_input_path> <output_path>");
            return -1;
        }

        String courseInputPath = args[0];
        String enrollmentInputPath = args[1];
        String outputPath = args[2];

        Configuration conf = getConf();
        conf.set("mapreduce.output.textoutputformat.separator", DATA_SEPARATOR);

        FileSystem fs = FileSystem.get(conf);
        if (fs.exists(new Path(outputPath))) {
            fs.delete(new Path(outputPath), true);
        }

        Job job = Job.getInstance(conf, "Course Enrollment Join");
        job.setJarByClass(EnrollmentJoinDriver.class);

        // Set up MultipleInputs
        MultipleInputs.addInputPath(job, new Path(courseInputPath), TextInputFormat.class, CourseMapper.class);
        MultipleInputs.addInputPath(job, new Path(enrollmentInputPath), TextInputFormat.class, EnrollmentMapper.class);

        job.setReducerClass(EnrollmentJoinReducer.class);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        job.setOutputFormatClass(TextOutputFormat.class);
        FileOutputFormat.setOutputPath(job, new Path(outputPath));

        boolean status = job.waitForCompletion(true);
        logger.info("Job completed with status: " + status);
        return status ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        int exitCode = ToolRunner.run(new EnrollmentJoinDriver(), args);
        System.exit(exitCode);
    }
}
