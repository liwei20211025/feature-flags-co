﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace FeatureFlagsCo.Messaging.ViewModels
{
    public class ExperimentIterationMessageViewModel
    {
        public string ExptId { get; set; }
        public string EnvId { get; set; }
        public int EventType { get; set; }
        public string EventName { get; set; }
        public int CustomEventTrackOption { get; set; }
        public string CustomEventUnit { get; set; }
        public int CustomEventSuccessCriteria { get; set; }
        public string StartExptTime { get; set; }
        public string EndExptTime { get; set; }
        public string IterationId { get; set; }

        public string FlagId { get; set; }

        public string BaselineVariation { get; set; }

        public List<string> Variations { get; set; }

        public double Power { get; set; } = 0.0;

        public double ExpectedExperimentEffect { get; set; } = 0.0;
    }
}