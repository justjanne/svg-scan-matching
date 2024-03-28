use fcmlib::Outline;
use serde::{Deserialize, Serialize};

use crate::{SegmentBezierDto, SegmentLineDto};

#[derive(Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum OutlineDto {
    Line {
        segments: Vec<SegmentLineDto>,
    },
    Bezier {
        segments: Vec<SegmentBezierDto>,
    },
}

impl From<&Outline> for OutlineDto {
    fn from(outline: &Outline) -> OutlineDto {
        match outline {
            Outline::Line(segments) => OutlineDto::Line {
                segments: segments.iter()
                    .map(|segment| SegmentLineDto::from(segment))
                    .collect()
            },
            Outline::Bezier(segments) => OutlineDto::Bezier {
                segments: segments.iter()
                    .map(|segment| SegmentBezierDto::from(segment))
                    .collect()
            },
        }
    }
}

impl Into<Outline> for &OutlineDto {
    fn into(self) -> Outline {
        match self {
            OutlineDto::Line { segments } => Outline::Line(
                segments.iter().map(|segment| segment.into()).collect()
            ),
            OutlineDto::Bezier { segments } => Outline::Bezier(
                segments.iter().map(|segment| segment.into()).collect()
            ),
        }
    }
}

impl Into<Outline> for OutlineDto {
    fn into(self) -> Outline {
        Into::into(&self)
    }
}
