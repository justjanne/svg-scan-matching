use fcmlib::SegmentBezier;
use serde::{Deserialize, Serialize};

use crate::PointDto;

#[derive(Serialize, Deserialize)]
pub struct SegmentBezierDto {
    control1: PointDto,
    control2: PointDto,
    end: PointDto,
}

impl SegmentBezierDto {
    pub fn from(segment: &SegmentBezier) -> SegmentBezierDto {
        SegmentBezierDto {
            control1: PointDto::from(&segment.control1),
            control2: PointDto::from(&segment.control2),
            end: PointDto::from(&segment.end),
        }
    }

    pub fn into(&self) -> SegmentBezier {
        SegmentBezier {
            control1: (&self.control1).into(),
            control2: (&self.control2).into(),
            end: (&self.end).into(),
        }
    }
}
