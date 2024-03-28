use std::fs::File;
use std::io::{BufReader, BufWriter};

use fcmlib::FcmFile;

pub use dto::*;
use error::FcmConversionError;

mod dto;
mod error;

fn from_json<T: AsRef<std::path::Path>>(source: T, target: T) -> Result<(), FcmConversionError> {
    let input = File::open(source.as_ref())?;
    let input = BufReader::new(input);
    let file: FileDto = serde_json::from_reader(input)?;
    let file: FcmFile = file.into();
    file.to_file(target.as_ref())?;
    Ok(())
}

fn to_json<T: AsRef<std::path::Path>>(source: T, target: T) -> Result<(), FcmConversionError> {
    let file = FcmFile::from_file(source)?;
    let file = FileDto::from(&file);
    let output = File::create(target.as_ref())?;
    let output = BufWriter::new(output);
    serde_json::to_writer(output, &file)?;
    Ok(())
}

fn main() -> Result<(), FcmConversionError> {
    let args: Vec<String> = std::env::args().collect();
    let source = &args[1];
    let target = &args[2];
    if source.ends_with(".fcm") && target.ends_with(".json") {
        to_json(source, target)
    } else if source.ends_with(".json") && target.ends_with(".fcm") {
        from_json(source, target)
    } else {
        panic!("Unexpected format conversion!")
    }
}
