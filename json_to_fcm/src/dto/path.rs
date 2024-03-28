use fcmlib::{Path, PathShape};
use serde::{Deserialize, Serialize};

use crate::{OutlineDto, PathFlagsDto, PointDto};

#[derive(Serialize, Deserialize)]
pub struct PathDto {
    flags: PathFlagsDto,
    start: PointDto,
    outlines: Vec<OutlineDto>,
}

impl TryFrom<&Path> for PathDto {
    type Error = ();

    fn try_from(path: &Path) -> Result<PathDto, Self::Error> {
        let shape = path.shape.as_ref().ok_or(())?;
        Ok(PathDto {
            flags: PathFlagsDto::from(&path.tool),
            start: PointDto::from(&shape.start),
            outlines: shape.outlines.iter()
                .map(|outline| OutlineDto::from(outline))
                .collect(),
        })
    }
}

impl Into<Path> for &PathDto {
    fn into(self) -> Path {
        Path {
            tool: (&self.flags).into(),
            shape: Some(PathShape {
                start: (&self.start).into(),
                outlines: self.outlines.iter().map(|outline| outline.into()).collect(),
            }),
            rhinestone_diameter: None,
            rhinestones: vec![],
        }
    }
}

impl Into<Path> for PathDto {
    fn into(self) -> Path {
        Into::into(&self)
    }
}
