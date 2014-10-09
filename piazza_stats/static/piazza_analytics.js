
(function(ps) {
    
    var PIAZZA_POST_BASE_URI = 'https://piazza.com/class/hx2lqx3ohi06j?cid=';
    
    
    ps.get_user = function(userid) {
        var username = '';
        $.ajax({
            type: "POST",
            url: "/get_users",
            data: JSON.stringify({users: [userid]}),
            dataType: "json",
            contentType: "application/json",
            success: function(json) {
                username = json.data[0];
            },
            async: false
        });
        return username;
    };
    
    
    var draw_bubbles = function(parentdiv) {
        var margin = {top: 20, right: 30, bottom: 40, left: 40},
            width = $("#mothership").width() - margin.left - margin.right,
            height = 700 - margin.top - margin.bottom;

        var x = d3.scale.linear()
            .range([0, width])
            .domain([0, 2399]); // 24-hour time scaled to base-100 instead of base-60

        var y = d3.scale.linear()
            .range([height, 0]);
        
        var r = d3.scale.linear()
            .range([3.5, 10]);
            
        var xHours = d3.scale.ordinal()
            .rangeRoundBands([0, width], 0/*.1*/);
        
        var yFrequency = d3.scale.linear()
            .range([height, 0]);
        
        var yFirstResponseDelta = d3.scale.linear()
            .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickFormat(function (d) {
                var h = d.toString();
                while (h.length < 4) h = "0" + h;
                return h.substr(0, 2) + ":" + h.substr(2,3);
             });

        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

        var yAxisFrequency = d3.svg.axis()
            .scale(yFrequency)
            .orient("right");

        d3.json('/posts-weights/json', function(error, data) {
            data = data.data;
            var highest_post_number = -1;
            
            data.forEach(function(d) {
                var zeropad2digits = function(n) {
                    return n < 10 ? "0"+n : n;
                };
                var date = new Date(d.created);
                d.created = date.toString();
                // scale minutes up to 100 instead of 60 to fill range of axis
                d.time = zeropad2digits(date.getHours()) + "" + (zeropad2digits(date.getMinutes() * 100/60));
                
                highest_post_number = Math.max(highest_post_number, d.nr);
            });
            
            var hours_avg = {};
            for (var h=0; h<24; h++) {
                hours_avg[h] = 0;
            }
            hours_avg = data.reduce(function(sofar, d) {
                sofar[+d.time.substr(0,2)] += 1;
                return sofar;
            }, hours_avg);
            hours_avg = d3.keys(hours_avg).map(function(h) {
                return {
                    "hour": h,
                    "frequency": hours_avg[h]
                }
            });
            
            
            $("<h2/>").text("Activity by Time of Day").appendTo($(parentdiv));
            
            $("<h3/>").text(data.length+" posts")
                .attr("title", "highest post #:" + highest_post_number).appendTo($("#infobar"));
            
            d3.json('/auto-update', function(err, update_data) {
                /*
                var delta = +update_data.data.update_count;
                
                $("<a/>")
                    .text(delta
                        ? 'Behind Piazza by ' + delta + ' post' + (delta > 1 ? 's' : '') + '.'
                        : 'Up to date with Piazza.')
                    .on("click", function() {
                        $.get('/auto-update');
                    })
                    .attr("href", "")
                    .attr("title", "Click to update.")
                    .hide().appendTo($("<p/>").appendTo($("#infobar"))).fadeIn(100);
                    */
            });


            var svg = d3.select(parentdiv).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
              .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
            
            
            var toggleLayer = function(evt) {
                $($(evt.target).data("chartlayer").selector).toggle();
            };
            
            
            ps.layers = [{name: "posts", selector: "svg .dot"},
               {name: "histogram", selector: "svg .bar.faded"},
               {name: "response times", selector: "svg .bar.responses"}
            ];
            
            _(ps.layers).each(function(d) {
                $("#layerpanel")
                    .append($("<li/>")
                        .append($("<label/>")
                            .text(d.name)
                            .click(toggleLayer)
                            .prepend($("<input/>")
                                .data("chartlayer", d)
                                .attr("type", "checkbox")
                                .prop("checked", 1)
                        )));
            });
            
            
            var tip = d3.tip()
                .attr("class", "d3-tip")
                .html(function(d) {
                    if (d.nr) {
                        var s = "<h3>" + d.subject + "</h3>"
                        s += "<p>Post #" + d.nr + " – " + d.created + "</p>";
                        s += d.content_preview;
                        return s;
                    } else if (d.frequency) {
                        return "<h4>" + d.frequency + " posts at " + (d.hour < 10 ? '0' : '') + d.hour + "00h</h4>";
                    } else if (d.avg_delta_inst) {
                        return "<h4>" + (d.avg_delta_inst / 60 / 60).toFixed(1) + "h avg instructor response</h4>";
                    } else if (d.avg_delta_stu) {
                        return "<h4>" + (d.avg_delta_stu / 60 / 60).toFixed(1) + "h avg student response</h4>";
                    } else
                        return "";
                });
                
            tip.direction(function(d) {
                // try to keep tooltip inside boundaries
                
                if (!this.cy) return 'n';
                
                var dir = this.cy.baseVal.value - 300 < 0
                        ? 's'
                        : 'n';
                
                if (this.cx.baseVal.value - 400 < 0)
                    dir += 'e';
                else if (this.cx.baseVal.value + 400 > $(parentdiv).width())
                    dir += 'w';
                
                return dir;
                
            });
        
            svg.call(tip);
            
            y.domain(d3.extent(data, function(d) { return d.unique_views; }));
            r.domain(d3.extent(data, function(d) { return d.tag_good_arr; }));
            xHours.domain(hours_avg.map(function(d) { return d.hour; }));
            yFrequency.domain([0, d3.max(hours_avg, function(d) { return d.frequency; })]);

            svg.selectAll(".bar.faded")
                .data(hours_avg)
                .enter().append("rect")
                .attr("class", "bar faded")
                .attr("x", function(d) { return xHours(d.hour); })
                .attr("width", xHours.rangeBand())
                .attr("y", function(d) { return yFrequency(d.frequency); })
                .attr("height", function(d) { return height - yFrequency(d.frequency); })
                .on("mouseover", tip.show)
                .on("mouseout", tip.hide);

            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis)
                .append("text")
                .attr("class", "label")
                .attr("x", width)
                .attr("y", 30)
                .style("text-anchor", "end")
                .text("Time of Day Created (HH:MM)");

            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis)
                .append("text")
                .attr("class", "label")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Unique Views");
            
            svg.append("g")
                .attr("class", "y axis")
                .attr("transform", "translate("+width+",0)")
                .call(yAxisFrequency)
                .append("text")
                .attr("class", "label")
                .attr("transform", "rotate(90)")
                .attr("y", 6)
                .attr("dy", ".71em")
                .text("Number of Posts (bars)");
            
            svg.append("g")
                .attr("class", "y axis")
                .attr("transform", "translate("+(width-20)+",0)")
                .append("text")
                    .attr("class", "label")
                    .attr("transform", "rotate(90)")
                    .attr("y", 6)
                    .attr("dy", ".71em")
                    .text("How long until first answer?");

            svg.selectAll(".dot")
                .data(data)
                .enter().append("circle")
                .attr("r", function(d) { return r(d.tag_good_arr); })
                .attr("cx", function(d) { return x(d.time); })
                .attr("cy", function(d) { return y(d.unique_views); })
                .on("click", function(d) { window.open(PIAZZA_POST_BASE_URI + d.nr); })
                .on("mouseover", tip.show)
                .on("mouseout", tip.hide)
                .attr("class", function(d) { return "dot" + (d.instructor_note ? " instructor" : "") + (d.private ? " private" : ""); });
//                    .append("svg:title")
//                        .text(function(d) { return "Post #" + d.nr; });
//                    .style("fill", function(d) { return color(d.species); });

/*
            var legend = svg.selectAll(".legend")
                .data(color.domain())
                .enter().append("g")
                .attr("class", "legend")
                .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

            legend.append("rect")
                .attr("x", width - 18)
                .attr("width", 18)
                .attr("height", 18)
                .style("fill", color);

            legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9)
                .attr("dy", ".35em")
                .style("text-anchor", "end")
                .text(function(d) { return d; });
                */
                
            d3.json("/time-until-responses", function(error, resp_data) {
                resp_data = resp_data.data;
                resp_data = _(resp_data).reduce(function(memo, d) {
                    if (!memo[d.created_hour])
                        memo[d.created_hour] = {freq: 0, responsedeltas_inst: [], responsedeltas_stu: []};
                    
                    if (d.timedelta_inst != -1) {
                        memo[d.created_hour].freq_inst++;
                        memo[d.created_hour].responsedeltas_inst.push(d.timedelta_inst);
                    }
                    if (d.timedelta_stu != -1) {
                        memo[d.created_hour].freq_stu++;
                        memo[d.created_hour].responsedeltas_stu.push(d.timedelta_stu);
                    }
                    return memo;
                }, {});
                
                yFirstResponseDelta.domain([0, d3.max(d3.values(resp_data), function(d) { return Math.max(d3.max(d.responsedeltas_inst),
                                                                                                          d3.max(d.responsedeltas_inst)); })]);

                resp_data_inst = _(d3.keys(resp_data)).map(function (hour) {
                    return {
                        hour: hour,
                        freq: resp_data[hour].freq,
                        avg_delta_inst: d3.mean(resp_data[hour].responsedeltas_inst) || 0
                    }
                });
                resp_data_stu = _(d3.keys(resp_data)).map(function (hour) {
                    return {
                        hour: hour,
                        freq: resp_data[hour].freq,
                        avg_delta_stu: d3.mean(resp_data[hour].responsedeltas_stu) || 0
                    }
                });

                svg.selectAll(".bar.responses.instructor")
                    .data(resp_data_inst)
                    .enter().append("rect")
                    .attr("class", "bar responses instructor")
                    .attr("x", function(d) { return xHours(d.hour) + xHours.rangeBand() * 3/16; })
                    .attr("width", xHours.rangeBand() * 4/16)
                    .attr("y", function(d) { return yFirstResponseDelta(d.avg_delta_inst); })
                    .attr("height", function(d) { return height - yFirstResponseDelta(d.avg_delta_inst); })
                    .on("mouseover", tip.show)
                    .on("mouseout", tip.hide);
                
                svg.selectAll(".bar.responses.stu")
                    .data(resp_data_stu)
                    .enter().append("rect")
                    .attr("class", "bar responses stu")
                    .attr("x", function(d) { return xHours(d.hour) + xHours.rangeBand() * 9/16; })
                    .attr("width", xHours.rangeBand() * 4/16)
                    .attr("y", function(d) { return yFirstResponseDelta(d.avg_delta_stu); })
                    .attr("height", function(d) { return height - yFirstResponseDelta(d.avg_delta_stu); })
                    .on("mouseover", tip.show)
                    .on("mouseout", tip.hide);
            });
        });
    };
    
    
    
    
    var draw_calendar = function(parentdiv) {
        var monthPath = function(t0) {
            var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
                d0 = +day(t0), w0 = +week(t0),
                d1 = +day(t1), w1 = +week(t1);
            return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
                + "H" + w0 * cellSize + "V" + 7 * cellSize
                + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
                + "H" + (w1 + 1) * cellSize + "V" + 0
                + "H" + (w0 + 1) * cellSize + "Z";
        };
        
        var margin = {top: 20, right: 20, bottom: 20, left: 20},
            width = $("#mothership").width() - margin.left - margin.right,
            height = 200 - margin.top - margin.bottom,
            cellSize = 17;
        
        var day = d3.time.format("%w"),
            week = d3.time.format("%U"),
            format = d3.time.format("%Y-%m-%d");
        
        
        d3.json("/calendar/json", function(error, json) {
            json = json.data;
            
            /*
            var years = _(json).chain()
                .map(function(val, d) {
                    return +d.substring(0,4); })   // get year part
                .uniq().value().sort();
            
            
            var year_months = _(years).reduce(function(memo, y) {
                memo[y] = [];
                return memo;
            }, {});*/
            
            var year_months = _(json).chain()
                .keys()
                .reduce(function(memo, d) {
                    var year  = +d.substring(0,4),
                        month = +d.substring(5,7);
                    if (!memo[year])
                        memo[year] = [];
                    if (!_(memo[year]).contains(month))
                        memo[year].push(month);
                    return memo;
                }, {})
                .value();
            
            var years = _(_(year_months).keys()).map(function(y){ return +y; });
            
            var months = function(year) {
                return d3.extent(d3.values(year_months[year]));
            }
            
            
                
            var svg = d3.select(parentdiv).selectAll("svg")
                .data(years)
                .enter().append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .attr("class", "RdYlGn")
                    .append("g")
                    .attr("transform", "translate("+((width-cellSize*53)/2)+","+(height-cellSize*7 - 1) + ")");
        
            svg.append("text")
                .attr("transform", "translate(-6," + cellSize * 3.5 + ")rotate(-90)")
                .style("text-anchor", "middle")
                .text(function(d) { return d; });


            var rect = svg.selectAll(".day")
                .data(function(year) { return d3.time.days(new Date(year, months(year)[0]-1, 1), new Date(year, months(year)[1], 1)); })
              .enter().append("rect")
                .attr("class", "day")
                .attr("width", cellSize)
                .attr("height", cellSize)
                .attr("x", function(d) { return week(d) * cellSize; })
                .attr("y", function(d) { return day(d) * cellSize; })
                .datum(format);
        
            rect.append("title")
                .text(function(d) { return d; });


            var g = svg.selectAll(".month")
                .data(function(year) { return d3.time.months(new Date(year, months(year)[0]-1, 1), new Date(year, months(year)[1], 1)); })
                .enter().append("g");

            g.append("text")
                .attr("transform", function(d) { return "translate(" + d3.time.format("%m")(d) * cellSize * 4.3 + ",-5)"})
                .attr("text-anchor", "end")
                .text(function(d) { return d3.time.format("%b")(d); });
            
            g.append("path")
                .attr("class", "month")
                .attr("d", monthPath);
            
            
            var color = d3.scale.quantize()
                .domain(d3.extent(d3.values(json)))
                .range(d3.range(11).map(function(d) {return "q" + d +"-11";}));
            
            rect.filter(function(d) { return json[d]})
                .attr("class", function(d) { return "day " + color(json[d]); })
                .select("title")
                .text(function(d) { return d + ": " + json[d]; });
        });
    };
    
    
    var render_posts_view = function(parentdiv) {
        d3.json("/posts", function(err, data) {
            data = data.data;
            data.forEach(function(d) {
                $("<li/>").text(d.result.nr)
                    .appendTo($(parentdiv));
            });
        });
    };
    
//    render_posts_view('#posts_view');
    
    
    draw_bubbles('#bubbles_chart');
    draw_calendar('#calendar_chart');
})(window.ps = window.ps || {});
