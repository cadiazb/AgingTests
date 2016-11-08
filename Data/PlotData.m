rawData = AgingTest20161107151259;

%% Get time axis
time = zeros(size(rawData,1),6);
for ii=1:size(rawData,1)
    time(ii,1) = str2num(rawData{ii,1}(1:4));
    time(ii,2) = str2num(rawData{ii,1}(5:6));
    time(ii,3) = str2num(rawData{ii,1}(7:8));
    time(ii,4) = str2num(rawData{ii,1}(10:11));
    time(ii,5) = str2num(rawData{ii,1}(12:13));
    time(ii,6) = str2num(rawData{ii,1}(14:15));
end
%% Convert to seconds from start
timeOrigin = time(1,3)*24*60*60 + time(1,4)*60*60 + time(1,5)*60 + time(1,6);
time(:,7) = (time(:,3)*24*60*60 + time(:,4)*60*60 + time(:,5)*60 + time(:,6)) - timeOrigin;

%% Import other data
thermoTemp = zeros(size(rawData,1),1);
bathTemp = zeros(size(rawData,1),1);
pumpON = zeros(size(rawData,1),1);
for ii=1:size(rawData,1)
thermoTemp(ii) = (rawData{ii,2});
bathTemp(ii) = (rawData{ii,3});
pumpON(ii) = strcmp(rawData{ii,4}, 'Pumping') + 2*strcmp(rawData{ii,4}, 'Purging');
end

%% Calculate real aged time
agedTime = time(2:end,7) - time(1:end-1,7);
agedTime2 = time(2:end,7) - time(1:end-1,7);
agedTime = agedTime .* 2.^((bathTemp(2:end)-37)/10);
agedTime2 = agedTime2 .* 2.^((77-37)/10);
fprintf('Aged time is %i days\n', floor(sum(agedTime)/(60*60*24)))
fprintf('Aged time is %i days if temp = 77C\n', floor(sum(agedTime2)/(60*60*24)))

%% Plots
clf
hold on
tickMarks = [0:1:(24*18)];
plot(time(:,7), thermoTemp, 'o')
plot(time(:,7), bathTemp, 'o')
% plot(time(:,7), smooth(bathTemp,20), 'o')
plot(time(:,7), pumpON*20)
set(gca, 'xtick', 3600*tickMarks)
set(gca, 'xtickLabel', num2cell(tickMarks))
xlabel('Hours since start')
ylabel('Temperature [C]')
ylim([0, 100])
text(12*3600,10,sprintf('Aged time is %i days', floor(sum(agedTime)/(60*60*24))), 'fontsize', 16)
text(12*3600,6,sprintf('or, Aged time is %i days if T=77C', floor(sum(agedTime2)/(60*60*24))), 'fontsize', 16)
