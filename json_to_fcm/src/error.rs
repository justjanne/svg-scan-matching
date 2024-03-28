use std::fmt::{Debug, Display, Formatter};

#[derive(Debug)]
pub enum FcmConversionError {
    IoError(std::io::Error),
    FcmError(fcmlib::Error),
    SerdeError(serde_json::Error),
}

impl Display for FcmConversionError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            FcmConversionError::IoError(err) => std::fmt::Display::fmt(&err, f),
            FcmConversionError::FcmError(err) => std::fmt::Display::fmt(&err, f),
            FcmConversionError::SerdeError(err) => std::fmt::Display::fmt(&err, f),
        }
    }
}

impl From<std::io::Error> for FcmConversionError {
    fn from(value: std::io::Error) -> Self {
        FcmConversionError::IoError(value)
    }
}

impl From<serde_json::Error> for FcmConversionError {
    fn from(value: serde_json::Error) -> Self {
        FcmConversionError::SerdeError(value)
    }
}

impl From<fcmlib::Error> for FcmConversionError {
    fn from(value: fcmlib::Error) -> Self {
        FcmConversionError::FcmError(value)
    }
}
